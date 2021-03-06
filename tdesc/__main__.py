#!/usr/bin/env python

"""
    tdesc
    
    cat filenames | python -m tdesc --model vgg16 --crow > feats
"""

import argparse

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--model', type=str, default='vgg16')
    parser.add_argument('--io-threads', type=int, default=3)
    parser.add_argument('--timeout', type=int, default=10)
    parser.add_argument('--target-dim', type=int, default=224)
    
    # VGG16 options
    parser.add_argument('--crow', action="store_true")
    
    # DlibFace options
    parser.add_argument('--dnn', action='store_true')
    parser.add_argument('--upsample', type=int, default=0)
    parser.add_argument('--batch-size', type=int, default=0)
    parser.add_argument('--num-jitters', type=int, default=10)
    parser.add_argument('--det-threshold', type=float, default=0.0)
    
    # Yolo options
    parser.add_argument('--yolo-cfg-path', type=str, required=False)
    parser.add_argument('--yolo-weight-path', type=str, required=False)
    parser.add_argument('--yolo-name-path', type=str, required=False)
    parser.add_argument('--yolo-thresh', type=float, default=0.1)
    parser.add_argument('--yolo-nms', type=float, default=0.3)
    
    args = parser.parse_args()
    
    if args.model == 'yolo':
        assert args.yolo_cfg_path is not None
        assert args.yolo_weight_path is not None
        assert args.yolo_nms is not None
    
    return args


if __name__ == "__main__":
    args = parse_args()
    
    if args.model == 'vgg16':
        from tdesc.workers import VGG16Worker
        worker = VGG16Worker(**{
            "crow" : args.crow,
            "target_dim" : args.target_dim,
        })
    elif args.model == 'dlib_face':
        if not args.batch_size:
            from tdesc.workers import DlibFaceWorker
            worker = DlibFaceWorker(**{
                "dnn" : args.dnn,
                "num_jitters" : args.num_jitters,
                "det_threshold" : args.det_threshold,
                "upsample" : args.upsample,
            })
        else:
            from tdesc.workers import DlibFaceBatchWorker
            worker = DlibFaceBatchWorker(**{
                "batch_size" : args.batch_size,
                "num_jitters" : args.num_jitters
            })
    elif args.model == 'yolo':
        from tdesc.workers import YoloWorker
        worker = YoloWorker(**{
            "cfg_path" : args.yolo_cfg_path,
            "weight_path" : args.yolo_weight_path,
            "name_path" : args.yolo_name_path,
            "thresh" : args.yolo_thresh,
            "nms" : args.yolo_nms,
        })
    else:
        print >> sys.stderr, "tdesc: Unknown model=%s" % args.model
        raise Exception()
    
    for w in worker.run(io_threads=args.io_threads, timeout=args.timeout):
        pass

