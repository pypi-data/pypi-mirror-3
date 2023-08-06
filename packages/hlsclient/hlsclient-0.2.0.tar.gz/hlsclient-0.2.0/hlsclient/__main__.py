import hashlib
import logging
import time
import csv

import helpers

from urllib2 import HTTPError

from balancer import Balancer
from consumer import consume
from discover import PlaylistDiscover
from cleaner import clean


def main():
    config = helpers.load_config()
    helpers.setup_logging(config)

    logging.debug('HLS CLIENT Started')
    destination = config.get('hlsclient', 'destination')
    clean_maxage = int(config.get('hlsclient', 'clean_maxage'))
    encrypt = config.getboolean('hlsclient', 'encrypt')

    # ignore all comma separated wildcard names for `clean` call
    if config.has_option('hlsclient', 'clean_ignore'):
        patterns = config.get('hlsclient', 'clean_ignore')
        ignores = list(csv.reader([patterns]))[0]
    else:
        ignores = []

    balancer = Balancer()

    while True:
        try:
            d = PlaylistDiscover(config)
            d.create_index_for_variant_playlists(destination)
            paths = d.playlist_paths

            logging.info(u'Discovered the following paths: %s' % paths.items())

            balancer.update(paths)

            for resource in balancer.actives:
                resource_path = str(resource)
                logging.debug('Consuming %s' % resource_path)
                try:
                    modified = consume(resource_path, destination, encrypt)
                except (HTTPError, IOError, OSError) as err:
                    logging.warning(u'Notifying error for resource %s: %s' % (resource_path, err))
                    balancer.notify_error(resource.server, resource.path)
                else:
                    if modified:
                        logging.info('Notifying content modified: %s' % resource)
                        balancer.notify_modified(resource.server, resource.path)
                    else:
                        logging.debug('Content not modified: %s' % resource)
            clean(destination, clean_maxage, ignores)
            time.sleep(2)
        except Exception as e:
            logging.info('ERRRRRRRR! An unknown error happened:\n%s\n' % e)
        except KeyboardInterrupt:
            # stop running
            logging.debug('Quitting...')
            return

if __name__ == "__main__":
    main()
