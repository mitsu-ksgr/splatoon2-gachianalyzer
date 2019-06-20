import cv2

from .video_analyzer import VideoAnalyzer


class AnalysisOrganizer:
    """
    VideoAnalyzer の結果を編成します.
    """

    def __organize(self):
        """
        self.result をイベント毎に編成しなおします.
        """
        events = []
        prev = self.result[0]
        for i in range(1, len(self.result)):
            # 前フレームと同じなら同じイベントとみなす.
            # 前フレームとイベントが変わったら記録する.
            if prev['event'] != self.result[i]['event']:
                end = self.result[i - 1]
                events.append({
                    'event': prev['event'],
                    'start_time': prev['time'],
                    'end_time': end['time'],
                    'start_frame': prev['frame'],
                    'end_frame': end['frame']
                })
                prev = self.result[i]
        return events

    def __init__(self, analyze_results):
        """
        analyze_results - VideoAnalyzer のリザルトの配列.
        #TODO 並列処理させない場合を考慮して、一次元配列だけを受け取れるようにする
        """
        self.result = sorted(
            [x for sub in analyze_results for x in sub],
            key = lambda x: x['frame']
        )
        self.events = self.__organize()

    def dump(self):
        for event in self.events:
            print('Time:{:4d} ~ {:4d}, Frame:{:5.0f} ~ {:5.0f}, Event={}'.format(
                event['start_time'], event['end_time'],
                event['start_frame'], event['end_frame'],
                event['event']
                ))

    def extract_battles(self):
        """
        試合部分（ガチマ開始〜リザルト表示）の開始時間, 試合時間を返します.
        """
        battles = []
        st_time = None
        battle_event = None
        for event in self.events:
            e = event['event']
            if e == 'Loading':
                st_time = event['end_time']
            elif e == 'ResultUdemae':
                battle_event = prev
                st_time = battle_event['start_time']
            elif e == 'ResultOkaneRank':
                # 直前にローディングを挟んで居ない場合、ロード画面後（バトル中）
                # から録画開始したと仮定し、battle_event の開始時刻を記録する
                if not st_time:
                    if not battle_event:
                        continue
                    st_time = battle_event['start_time']

                diff = int(event['end_time']) - int(st_time)
                battles.append((st_time, diff))
                st_time, battle_event = None, None

            elif e in ['LobbyStandby', 'LobbyModeSelect', 'LobbyFindBattle']:
                st_time, battle_event = None, None
            else:
                pass
            prev = event
        return battles


