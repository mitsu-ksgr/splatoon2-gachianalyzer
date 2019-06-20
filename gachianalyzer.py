import argparse
import cv2
import time

from multiprocessing import Process, Lock, Pool

from gachianalyzer.analysis_organizer import AnalysisOrganizer
from gachianalyzer.video_analyzer import VideoAnalyzer


def analyze_video_wrapper(args):
    return VideoAnalyzer(args[0], **args[1]).analyze()


def parallel_analyze(video_path, pnum, analyze_interval=1):
    """
    video_path - ガチマ動画へのパス
    pnum - 並列数
    analyze_interval - フレーム分析精度
    """
    if pnum <= 1:
        raise ValueError('Error, pnum must be an integer greater than 1')

    # video の総フレーム数を取得
    video = cv2.VideoCapture(video_path)
    total_frame = video.get(cv2.CAP_PROP_FRAME_COUNT)
    fps = video.get(cv2.CAP_PROP_FPS)

    # プロセス毎に処理させたいフレーム
    args_list = []
    for i in range(pnum):
        st = i * int(total_frame / pnum)
        en = st + int(total_frame / pnum)
        if i == (pnum - 1): # 最後の要素
            en += int(total_frame % pnum)
        args_list.append((video_path, {
            'frame_range': range(st, en, analyze_interval)
        }))

    ret = Pool(processes=pnum).map(analyze_video_wrapper, args_list)
    ao = AnalysisOrganizer(ret)
    #ao.dump()
    for battle in ao.extract_battles():
        print("{},{}".format(*battle))


def main(video_path, pnum, analyze_interval):
    #t_st = time.time()
    parallel_analyze(video_path, pnum, analyze_interval)
    #t_en = time.time()
    #print('ProcessTime: {}:{}'.format(
    #    int((t_en - t_st) / 60),
    #    int((t_en - t_st) % 60)
    #    ))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        usage='get_cut_cmd.py video_path [-h]',
        description='Gachima Video Analyzer')
    parser.add_argument('video_path',
        help='path to the gachima video.')
    parser.add_argument('-p', '--process', type=int, default=1,
        help='Number of processes for multi processing')
    parser.add_argument('-i', '--frameinterval', type=int, default=1,
        help='Frame interval to analyze.')

    args = parser.parse_args()
    main(args.video_path, args.process, args.frameinterval)

