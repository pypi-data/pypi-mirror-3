#!/usr/bin/env python
# encoding: utf-8
from django.contrib.auth.models import User
from django.core.management.base import CommandError
from flickr.management.commands import FlickrCommand
from flickr.models import FlickrUser, Photo, JsonCache, PhotoSet, Collection
from flickr.shortcuts import get_all_photos, get_photo_details_jsons, \
    get_photosets_json, get_photoset_photos_json, get_user_json, \
    get_collections_tree_json
from optparse import make_option
import datetime
import time


class Command(FlickrCommand):
    
    help_text = 'Django-Flickr\n\nRun "./manage.py flickr_sync --help" for details, \nor rtfm at http://bitbucket.org/zalew/django-flickr/ \n\n'
    
    option_list = FlickrCommand.option_list + (
        
        make_option('--initial', '-i', action='store_true', dest='initial', default=None,
            help='Initial sync. For improved performance it assumpts db flickr tables are empty and blindly hits create().'),
        
        make_option('--days', '-d', action='store', dest='days', default=None,
            help='Sync photos from the last n days. Useful for cron jobs.'),       
                
        make_option('--user', '-u', action='store', dest='user_id', default=1,
            help='Sync for a particular user. Default is 1 (in most cases it\'s the admin and you\'re using it only for yourself).'),
                                             
        make_option('--page', action='store', dest='page', default=None,
            help='Grab a specific portion of photos. To be used with --per_page.'), 
                                                  
        make_option('--per_page', action='store', dest='per_page', default=20,
            help='How many photos per page should we grab? Set low value (10-50) for daily/weekly updates so there is less to parse,\n\
set high value (200-500) for initial sync and big updates so we hit flickr less.'),                                       
                                             
        make_option('--force_update', action='store_true', dest='force_update', default=False,
            help='If photo in db, override with new data.'),

        
        make_option('--photosets', action='store_true', dest='photosets', default=False,
            help='Sync photosets (only photosets, no photos sync action is run). Photos must be synced first. If photo from photoset not in our db, it will be ommited.'),
        
        make_option('--collections', action='store_true', dest='collections', default=False,
            help='Sync collections. Photos and sets must be synced first.'),
                      
        make_option('--photos', action='store_true', dest='photos', default=False,
            help='Sync photos (only photos, no photosets sync action is run).'),

        make_option('--update_photos', action='store_true', dest='update_photos', default=False,
            help='Update photos when updating a photoset.'),

        make_option('--update_tags', action='store_true', dest='update_tags', default=False,
            help='Update tags when updating a photo.'),

    
        make_option('--test', '-t', action='store_true', dest='test', default=False,
            help='Test/simulate. Don\'t write results to db.'),         
         
        )


    
    
    def handle(self, *args, **options):
        super(Command, self).handle(*args, **options)
        
        t1 = time.time()
        
        """default behavior: sync pics newer than the newest and user info"""
        self.user_info(**options)        
        
        self.user_photos(**options)
                
        if options.get('photosets'):
            self.user_photosets(**options)
        
        if options.get('collections'):
            self.user_collections(**options)
        
    
        self.flickr_user.save() # bump last_sync
            
        t2 = time.time()
        self.v('Exec time: '+str(round(t2-t1)), 0)
        return 'Sync end'
    
    
    def user_info(self, **options):
        flickr_user = self.flickr_user
        self.v('Syncing user info', 0)
        self.v('- getting user info for %s...' % flickr_user.user, 1)
        info = get_user_json(nsid=flickr_user.nsid, token=flickr_user.token)
        length = len(info)
        if length > 0:
            self.v('- got user info, it might take a while...', 1)
            if not options.get('test', False):
                FlickrUser.objects.update_from_json(pk=flickr_user.pk, info=info)
            else:
                self.v('-- got data for user', 1)
        self.v('COMPLETE: user info sync', 0)
    
    
    def user_photos(self, **options):        
        flickr_user = self.flickr_user
        self.v('Syncing user photos', 0)
        self.v('- getting user photos list...', 1)
        page = options.get('page')
        per_page = options.get('per_page')
        min_upload_date = None
        if options.get('days'):
            days = int(options.get('days'))
            min_upload_date = (datetime.date.today() - datetime.timedelta(days)).isoformat()
        else:
            try:
                self.v('- fetching since last sync', 1)
                min_upload_date = flickr_user.last_sync
            except:
                pass
        photos = get_all_photos(nsid=flickr_user.nsid, token=flickr_user.token, 
                        page=page, per_page=per_page, min_upload_date=min_upload_date)
        length = len(photos)
        if length > 0:
            self.v('- got %d photos, fetching info, it might take a while...' % length, 1)
            time.sleep(3)
            i = 0
            for photo in photos:
                try:
                    self.v('- fetching info for photo #%s "%s"' % (photo.id, photo.title), 1)
                    info, sizes, exif, geo = get_photo_details_jsons(photo_id=photo.id, token=flickr_user.token)
                    if not options.get('test', False):
                        if options.get('initial', False):
                            #blindly create for initial sync (assumpts table is empty)
                            self.v('inserting photo #%s "%s"' % (photo.id, photo.title), 1)
                            Photo.objects.create_from_json(flickr_user=flickr_user, info=info, sizes=sizes, exif=exif, geo=geo)
                        else:                            
                            if not Photo.objects.filter(flickr_id=photo.id):
                                self.v('- inserting photo #%s "%s"' % (photo.id, photo.title), 1)
                                Photo.objects.create_from_json(flickr_user=flickr_user, info=info, sizes=sizes, exif=exif, geo=geo)
                            else:
                                self.v('- record found for photo #%s "%s"' % (photo.id, photo.title), 1)
                                if options.get('force_update', False): 
                                    self.v('- updating photo #%s "%s"' % (photo.id, photo.title), 1)                            
                                    Photo.objects.update_from_json(flickr_id=photo.id, info=info, sizes=sizes, exif=exif, geo=geo, update_tags=options.get('update_tags', False))
                    else:
                        self.v('- got data for photo #%s "%s"' % (photo.id, photo.title), 1)
                except Exception as e:
                    self.v('- ERR failing silently exception "%s"' % (e), 1)
                    # in case sth got wrong with a data set, let's log all the data to db and not break the ongoing process
                    try:                
                        JsonCache.objects.create(flickr_id=photo.id, info=info, sizes=sizes, exif=exif, geo=geo, exception=e)
                    except Exception as e2:
                        #whoa sth is really messed up
                        JsonCache.objects.create(flickr_id=photo.id, exception=e2)
                i += 1
                if i % 10 == 0:
                    self.v('- %d photos info fetched, %d to go'  % (i, length-i), 1)
                    time.sleep(2) #so we don't get our connections dropped by flickr api'
                if i % 100 == 0:
                    time.sleep(3)
        else:
            self.v('- nothing to sync', 0)
        self.v('COMPLETE: user photos sync', 0)        
        
    
    def user_photosets(self, **options):
        flickr_user = self.flickr_user
        self.v('Syncing photosets', 0)        
        self.v('- getting user photosets list...', 1)
        sets = get_photosets_json(nsid=flickr_user.nsid, token=flickr_user.token).photosets.photoset
        length = len(sets)
        if length > 0:
            self.v('- got %d photosets, fetching photos, it might take a while...' % length, 1)
            time.sleep(1)
            i = 0
            for s in sets:
                photos = get_photoset_photos_json(photoset_id=s.id, token=flickr_user.token)
                if not options.get('test', False):
                    if options.get('initial', False):
                        PhotoSet.objects.create_from_json(flickr_user=flickr_user, info=s, photos=photos)
                    else:
                        if not PhotoSet.objects.filter(flickr_id=s.id):
                            PhotoSet.objects.create_from_json(flickr_user=flickr_user, info=s, photos=photos)
                        else:
                            if options.get('force_update', False):
                                PhotoSet.objects.update_from_json(flickr_id=s.id, info=s, photos=photos, update_photos=options.get('update_photos', False))
                i += 1
                if i % 10 == 0:
                    self.v('- %d photosets fetched, %d to go'  % (i, length-i), 1)
                    time.sleep(2) #so we don't get our connections dropped by flickr api'
        else:
            self.v('- nothing to sync', 1)
        self.v('COMPLETE: user photosets sync', 0)
        
    
    def user_collections(self, **options):
        flickr_user = self.flickr_user
        self.v('Syncing collections', 0)
        tree = get_collections_tree_json(nsid=flickr_user.nsid, token=flickr_user.token)
        length = len(tree)
        if length > 0:
            self.v('- got %d collections in root of tree for user' % length, 1)
            if not options.get('test', False):
                    if options.get('initial', False):
                        Collection.objects.create_from_usertree_json(flickr_user, tree)
                    else:
                        Collection.objects.create_or_update_from_usertree_json(flickr_user, tree)                
        else:
            self.v('- nothing to sync', 1)
        self.v('COMPLETE: user collections sync', 0)
        
        
        
        
        
        
        
    
