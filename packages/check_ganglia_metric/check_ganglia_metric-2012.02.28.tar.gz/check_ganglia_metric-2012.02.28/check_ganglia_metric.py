#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import os
import pickle
import pprint
import random
import socket
import sys
import tempfile
import time
from xml.etree.cElementTree import XML


__app_name__     = 'check_ganglia_metric'
__version__      = '2012.02.28'
__author__       = 'Michael Paul Thomas Conigliaro'
__author_email__ = 'mike [at] conigliaro [dot] org'
__description__  = 'Ganglia metric check plugin for Nagios'
__url__          = 'http://github.com/mconigliaro/check_ganglia_metric'


class GangliaMetrics(object):
    """Ganglia metric check class"""

    class Error(Exception):
        """Base exception for all GangliaMetrics errors"""

        def __init__(self, message, log_level='error'):
            """Log all exception messages"""

            getattr(logging.getLogger(__name__), log_level)(message)
            super(GangliaMetrics.Error, self).__init__(message)

    class GmetadError(Error):
        """Base class for all gmetad errors"""

    class GmetadNetworkError(GmetadError):
        """Raised on gmetad network errors"""

    class GmetadNoDataError(GmetadError):
        """Raised when no data is received from gmetad"""

    class GmetadXmlError(GmetadError):
        """Raised on gmetad XML parse errors"""

    class CacheError(Error):
        """Base class for all cache errors"""

    class CacheExpiredError(CacheError):
        """Raised on cache expiration"""

        def __init__(self, message):
            """Override log level for these errors"""

            super(GangliaMetrics.CacheExpiredError, self).__init__(message, 'info')

    class CacheReadError(CacheError):
        """Raised on cache read errors"""

    class CacheWriteError(CacheError):
        """Raised on cache write errors"""

    class CacheLockError(CacheWriteError):
        """Raised on cache lock errors"""

        def __init__(self, message):
            """Override log level for these errors"""

            super(GangliaMetrics.CacheLockError, self).__init__(message, 'info')

    class StaleCacheLockError(CacheWriteError):
        """Raised when stale cache lock is detected"""

    class CacheUnlockError(CacheWriteError):
        """Raised on cache unlock errors"""

    class MetricNotFoundError(Error):
        """Raised when metric host/name is not found"""

    class MetricsExpiredError(Error):
        """Raised on metric expiration"""

    def __init__(self, gmetad_host, gmetad_port, gmetad_timeout, cache_path,
                 cache_ttl, cache_ttl_splay, cache_grace, metrics_max_age, debug_level):
        """Initialization"""

        self.gmetad_host     = gmetad_host
        self.gmetad_port     = int(gmetad_port)
        self.gmetad_timeout  = float(gmetad_timeout)
        self.cache_path      = cache_path
        self.cache_lock_path = '%s.lock' % cache_path

        splay_secs           = float(cache_ttl) * float(cache_ttl_splay) / 2
        self.cache_ttl       = random.uniform(float(cache_ttl) - splay_secs,
                                              float(cache_ttl) + splay_secs)
        self.cache_grace     = float(cache_grace)
        self.metrics_max_age = float(metrics_max_age)

        # Configure debug logging
        self.log = logging.getLogger(__name__)
        if debug_level:
            console_logger = logging.StreamHandler()
            console_logger.setFormatter(
                logging.Formatter("%(asctime)s %(levelname)s: %(message)s"))
            self.log.addHandler(console_logger)
            try:
                log_level = getattr(logging, [None, 'INFO', 'DEBUG'][debug_level])
            except IndexError:
                log_level = logging.DEBUG
            self.log.setLevel(log_level)
        else:
            self.log.addHandler(logging.FileHandler(os.devnull))

    def get_value(self, metric_host, metric_name):
        """Return a value for the specified metric host/name"""

        try:
            metrics = self._cache_read()
        except self.CacheError:
            try:
                self._cache_lock()
                try:
                    metrics = self._gmetad_parse(self._gmetad_read())
                    self._cache_write(metrics)
                finally:
                    self._cache_unlock()
            except (self.CacheLockError, self.GmetadError):
                self.log.info('Attempting to force read from cache')
                metrics = self._cache_read(ignore_expiration=True)

        self.log.info('Found metrics for %d hosts', len(metrics))

        if self.log.isEnabledFor(logging.DEBUG):
            self.log.debug("Dumping metrics\n%s", pprint.pformat(metrics))

        if metric_host not in metrics:
            raise self.MetricNotFoundError('Host "%s" not found' % metric_host)
        elif metric_name not in metrics[metric_host]['metrics']:
            raise self.MetricNotFoundError('Metric "%s" for host "%s" not found' %
                                          (metric_name, metric_host))

        metrics_age = time.time() - int(metrics[metric_host]['reported'])
        if (metrics_age > self.metrics_max_age):
            raise self.MetricsExpiredError('Metrics for %s expired by %f seconds' %
                                          (metric_host, metrics_age - self.metrics_max_age))
        else:
            self.log.info('Metrics for %s expire in %f seconds' %
                         (metric_host, self.metrics_max_age - metrics_age))

        return metrics[metric_host]['metrics'][metric_name]

    def _gmetad_read(self):
        """Read XML data from Ganglia meta daemon (gmetad)"""

        self.log.info('Connecting to gmetad at %s:%d',
                      self.gmetad_host, self.gmetad_port)

        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        except StandardError, e:
            raise self.GmetadNetworkError('Error while creating socket: %s' % e)

        try:
            sock.settimeout(self.gmetad_timeout)
            sock.connect((self.gmetad_host, self.gmetad_port))
        except StandardError, e:
            raise self.GmetadNetworkError('Error while connecting to gmetad at %s:%d: %s' %
                                         (self.gmetad_host, self.gmetad_port, e))

        self.log.info('Reading gmetad XML')

        try:
            xml_data = ''
            buffer = sock.recv(4096)
            while len(buffer):
                xml_data += buffer
                buffer = sock.recv(4096)
            sock.close()
            msg = 'Read %s bytes from gmetad' % len(xml_data)
            if len(xml_data):
                self.log.info(msg)
            else:
                raise self.GmetadNoDataError('%s (Hint: Check trusted_hosts and/or all_trusted in gmetad.conf)' % msg)
        except StandardError, e:
            raise self.GmetadNetworkError('Error while reading gmetad XML from %s:%d: %s' %
                                         (self.gmetad_host, self.gmetad_port, e))

        return xml_data

    def _gmetad_parse(self, xml_data):
        """Parse metrics from XML data"""

        self.log.info('Parsing %d bytes of gmetad XML', len(xml_data))

        metrics = {}
        try:
            for host in XML(xml_data).findall('GRID/CLUSTER/HOST'):
                host_name = host.get('NAME')
                metrics[host_name] = {
                    'reported': host.get('REPORTED'),
                    'metrics' : {}
                }
                for metric in host.findall('METRIC'):
                    metric_name = metric.get('NAME')
                    metrics[host_name]['metrics'][metric_name] = {
                        'title': metric_name,
                        'units': metric.get('UNITS'),
                        'value': metric.get('VAL')
                    }
                    for extra_data in metric.findall('EXTRA_DATA/EXTRA_ELEMENT'):
                        if extra_data.get('NAME') == 'TITLE':
                            metrics[host_name]['metrics'][metric_name]['title'] = extra_data.get('VAL')
                            break # No need for further searching

        except Exception, e:
            raise self.GmetadXmlError('Error while parsing gmetad XML: %s' % e)

        return metrics

    def _cache_read(self, ignore_expiration=False):
        """Read metrics from cache"""

        self.log.info('Checking cache at %s', self.cache_path)

        try:
            cache_age = time.time() - os.path.getmtime(self.cache_path)
        except StandardError, e:
            raise self.CacheReadError('Error while checking age of cache at %s: %s' %
                                     (self.cache_path, e))

        if cache_age > self.cache_ttl + self.cache_grace or \
           (cache_age > self.cache_ttl and not ignore_expiration):
            raise self.CacheExpiredError('Cache is expired by %f seconds' %
                                        (cache_age - self.cache_ttl))
        else:
            self.log.info('Cache expires in %f seconds' %
                         (self.cache_ttl - cache_age))
            try:
                cache = open(self.cache_path, 'rb')
                metrics = pickle.load(cache)
                cache.close()
            except StandardError, e:
                raise self.CacheReadError('Error while reading from cache at %s: %s' %
                                         (self.cache_path, e))

        return metrics

    def _cache_write(self, metrics):
        """Write metrics to cache"""

        self.log.info('Updating cache at %s', self.cache_path)

        try:
            cache_tmp = tempfile.mkstemp(dir=os.path.dirname(self.cache_path))
        except StandardError, e:
            raise self.CacheWriteError('Error while creating temp file: %s' % e)

        try:
            self.log.info('Writing %d bytes to cache', os.write(cache_tmp[0],
                          pickle.dumps(metrics, pickle.HIGHEST_PROTOCOL)))
            os.close(cache_tmp[0])
            os.rename(cache_tmp[1], self.cache_path)
        except StandardError, e:
            os.unlink(cache_tmp[1])
            raise self.CacheWriteError('Error while updating cache at %s: %s' %
                                      (self.cache_path, e))

    def _cache_lock(self):
        """Create the cache lock"""

        self.log.info('Creating cache lock at %s', self.cache_lock_path)

        try:
            os.mkdir(self.cache_lock_path)
        except StandardError, e:
            try:
                cache_lock_age = time.time() - os.path.getmtime(self.cache_lock_path)
            except StandardError, e:
                raise self.CacheLockError('Error while checking age of cache lock at %s: %s' %
                                         (self.cache_lock_path, e))

            if cache_lock_age > self.cache_ttl + self.cache_grace:
                try:
                    os.utime(self.cache_lock_path, None)
                except StandardError:
                    raise self.StaleCacheLockError('Stale cache lock found at %s' %
                                                   self.cache_lock_path)
            else:
                raise self.CacheLockError('Error while creating cache lock at %s: %s' %
                                         (self.cache_lock_path, e))

    def _cache_unlock(self):
        """Remove the cache lock"""

        self.log.info('Removing cache lock at %s', self.cache_lock_path)

        try:
            os.rmdir(self.cache_lock_path)
        except StandardError, e:
            if os.path.exists(self.cache_lock_path):
                raise self.CacheUnlockError('Error while removing cache lock at %s: %s' %
                                           (self.cache_lock_path, e))


if __name__ == '__main__':

    try:
        from NagAconda import Plugin
    except ImportError, e:
        print('%s (Hint: "pip install NagAconda" or "easy_install NagAconda")' % e)
        sys.exit(2)

    # Initialize plugin
    plugin = Plugin(__description__, __version__)
    cache_path = os.path.join(os.path.expanduser('~'), '.check_ganglia_metric.cache')
    plugin.add_option('d', 'gmetad_host',
                      'Ganglia meta daemon host (default: localhost)',
                      default='localhost')
    plugin.add_option('p', 'gmetad_port',
                      'Ganglia meta daemon port (default: 8651)',
                      default=8651)
    plugin.add_option('t', 'gmetad_timeout',
                      'Ganglia meta daemon connection/read timeout in seconds (default: 2)',
                      default=2)
    plugin.add_option('f', 'cache_path',
                      'Cache path (default: %s)' % cache_path,
                      default=cache_path)
    plugin.add_option('l', 'cache_ttl',
                      'Cache TTL in seconds (default: 60)',
                      default=60)
    plugin.add_option('s', 'cache_ttl_splay',
                      'Cache TTL splay factor (default: 0.5)',
                      default=0.5)
    plugin.add_option('g', 'cache_grace',
                      'Cache grace period in seconds (default: 60)',
                      default=60)
    plugin.add_option('r', 'metrics_max_age',
                      'Metrics maximum age in seconds (default: 300)',
                      default=300)
    plugin.add_option('a', 'metric_host',
                      'Metric host address',
                      required=True)
    plugin.add_option('m', 'metric_name',
                      'Metric name',
                      required=True)

    plugin.enable_status('warning')
    plugin.enable_status('critical')

    plugin.start()

    # Execute check
    try:
        value = GangliaMetrics(gmetad_host=plugin.options.gmetad_host,
                               gmetad_port=plugin.options.gmetad_port,
                               gmetad_timeout=plugin.options.gmetad_timeout,
                               cache_path=plugin.options.cache_path,
                               cache_ttl=plugin.options.cache_ttl,
                               cache_ttl_splay=plugin.options.cache_ttl_splay,
                               cache_grace=plugin.options.cache_grace,
                               metrics_max_age=plugin.options.metrics_max_age,
                               debug_level=plugin.options.verbose).get_value(
                                  metric_host=plugin.options.metric_host,
                                  metric_name=plugin.options.metric_name)

        plugin.set_status_message('%s = %s %s' % (value['title'],
                                                  value['value'],
                                                  value['units']))

        if value['units'].upper() in ('B', 'KB', 'MB', 'GB', 'TB') or \
           value['units'].lower() in ('s', 'ms', 'us', 'ns', '%'):
            plugin.set_value(plugin.options.metric_name, value['value'],
                             scale=value['units'])
        else:
            plugin.set_value(plugin.options.metric_name, value['value'])

    except (GangliaMetrics.MetricNotFoundError), e:
         plugin.unknown_error(str(e))
    except (Exception), e:
        print(e)
        sys.exit(2)

    # Print results
    plugin.finish()
