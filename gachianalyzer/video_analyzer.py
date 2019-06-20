import cv2

from .frame_analyzer import FrameAnalyzer


class VideoAnalyzer:
    """
    ガチマ動画を分析します.
    """

    def __frame_to_sec(self, frame_no):
        return int(round(frame_no / self.video_fps, 3))

    def __init__(self, video_path, **opt):
        """
        opt -- オプション
        opt['frame_range'] -- 処理したいフレーム区間を表した range オブジェクト.
            range の step を指定すいることで、分析精度を調整します.
            (stepが大きいほど分析するフレーム数が減り処理負荷も小さくなりますが、
             その分精度も下がります)
        """
        self.video_path = video_path
        self.video = cv2.VideoCapture(self.video_path)
        self.total_frame = self.video.get(cv2.CAP_PROP_FRAME_COUNT)
        self.video_fps = self.video.get(cv2.CAP_PROP_FPS)
        self.frame_analyzer = FrameAnalyzer()
        # options
        self.analyze_frame_range = opt.get('frame_range', range(0, int(self.total_frame)))

    def analyze(self):
        events = []
        for frame_no in self.analyze_frame_range:
            self.video.set(cv2.CAP_PROP_POS_FRAMES, frame_no)
            ret, frame = self.video.read()
            if not ret:
                continue

            event = self.frame_analyzer.analyze(frame)
            events.append({
                'frame': frame_no,
                'event': event,
                'time': self.__frame_to_sec(frame_no)
            })

            # Debug Log
            #print('{:5d}/{:5d}: {:10.4f}s {}'.format(
            #    int(frame_no), int(self.total_frame),
            #    frame2sec(frame_no, self.video_fps), event))

        self.video.release()
        return events

