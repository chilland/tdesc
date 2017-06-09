#!/usr/bin/env python

"""
    workers.py
"""

import os
import sys
import urllib
import cStringIO
import numpy as np

from base import BaseWorker

def import_dlib():
    global dlib
    global h5py
    global io
    global color
    import dlib
    from skimage import io
    from skimage import color

class DlibFaceWorker(BaseWorker):
    """ 
        compute dlib face descriptors 
    """
    
    def __init__(self, detect=True, num_jitters=10, dnn=False):
        import_dlib()
        
        ppath = os.path.join(os.environ['HOME'], '.tdesc')
        
        if not dnn:
            self.detector = dlib.get_frontal_face_detector()
        else:
            detpath = os.path.join(ppath, 'models/dlib/mmod_human_face_detector.dat')
            self.detector = dlib.face_detection_model_v1(detpath)
        
        shapepath = os.path.join(ppath, 'models/dlib/shape_predictor_68_face_landmarks.dat')
        self.sp = dlib.shape_predictor(shapepath)
        
        facepath = os.path.join(ppath, 'models/dlib/dlib_face_recognition_resnet_model_v1.dat')
        self.facerec = dlib.face_recognition_model_v1(facepath)
        
        self.detect = detect
        self.num_jitters = num_jitters
        
        print >> sys.stderr, 'DlibFaceWorker: ready (detect=%d | num_jitters=%d)' % (int(detect), int(num_jitters))
    
    def imread(self, path):
        img = io.imread(path)
        if img.shape[-1] == 4:
            img = color.rgba2rgb(img)
        elif len(img.shape) == 2:
            img = color.grey2rgb(img)
        
        if self.detect:
            if not self.dnn:
                dets = self.detector(img, 1)
            else:
                dets = self.detector.detect(img)
        else:
            dets = [dlib.rectangle(top=0, bottom=img.shape[0], left=0, right=img.shape[1])]
        
        return img, dets
    
    def featurize(self, path, obj, return_feat=False):
        img, dets = obj
        feats = []
        for k,d in enumerate(dets):
            shape = self.sp(img, d)
            face_descriptor = self.facerec.compute_face_descriptor(img, shape, self.num_jitters)
            
            if not return_feat:
                print '\t'.join((
                    path, 
                    str(k),
                    '\t'.join(map(str, [d.top(),d.bottom(),d.left(),d.right()])), 
                    '\t'.join(map(str, face_descriptor))
                ))
                sys.stdout.flush()
            else:
                feats.append({
                    "k" : k,
                    "bbox" : [d.top(),d.bottom(),d.left(),d.right()],
                    "desc" : face_descriptor
                })
        
        if return_feat:
            return path, feats
    
    def close(self):
        print >> sys.stderr, 'DlibFaceWorker: terminating'
