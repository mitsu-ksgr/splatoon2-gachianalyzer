import cv2
import numpy as np
import os

TEMPLATE_RESOLUTION = [720, 1280]

class TemplatePattern:
    class FileReadError(Exception):
        def __init__(self, path):
            self.path = path

        def __str__(self):
            return 'Failed to read template file: {}'.format(self.path)

    def __init__(self, event, path, threshold):
        self.event = event
        self.threshold = threshold
        self.template = cv2.imread(path, cv2.IMREAD_GRAYSCALE)
        if self.template is None:
            raise TemplatePattern.FileReadError(path)

    def is_match(self, gray_frame):
        res = cv2.matchTemplate(gray_frame, self.template, cv2.TM_CCOEFF_NORMED)
        loc = np.where(res >= self.threshold)

        # loc は array を２つもった tuple.
        # マッチしたなかった場合、loc は ([], []) になる
        #is_match = all(x for x in map(lambda x: len(x) > 0, loc))
        is_match = ((len(loc[0]) > 0) and (len(loc[1]) > 0))
        return is_match


class FrameAnalyzer:
    """
    ガチマ動画のフレームを分析します.
    """

    @classmethod
    def default_template_pattern_list(cls, dir_path = None):
        """
        デフォルトのテンプレート画像へのパスを返します.

        -- dir_path デフォルト以外の画像を使用したい場合に指定
        """
        if not dir_path:
            dir_path = '{}/templates'.format(os.path.dirname(__file__))

        return [
            { 'event': 'LobbyFindBattle',   'threshold': 0.7,   'path': '{}/lobby_find_battle.png'.format(dir_path) },
            { 'event': 'LobbyModeSelect',   'threshold': 0.7,   'path': '{}/lobby_mode_select.png'.format(dir_path) },
            { 'event': 'LobbyStandby',      'threshold': 0.7,   'path': '{}/lobby_standby.png'.format(dir_path) },
            { 'event': 'ResultContinue',    'threshold': 0.7,   'path': '{}/result_continue.png'.format(dir_path) },
            { 'event': 'ResultOkaneRank',   'threshold': 0.7,   'path': '{}/result_okane_rank.png'.format(dir_path) },
            { 'event': 'ResultUdemae',      'threshold': 0.7,   'path': '{}/result_stat_udemae.png'.format(dir_path) },

            # テンプレート画像が小さいパターンは、その分処理負荷も大きくなる.
            # ので、あんまり意味ないやつは一旦オフ.
            #{ 'event': 'ResultLose',        'threshold': 0.7,   'path': '{}/result_lose.png'.format(dir_path) },
            #{ 'event': 'ResultWin',         'threshold': 0.7,   'path': '{}/result_win.png'.format(dir_path) },
        ]

    def __init__(self, opt={}):
        self.templates = []
        tl = FrameAnalyzer.default_template_pattern_list(opt.get('dir_path'))
        for t in tl:
            self.templates.append(TemplatePattern(
                t['event'], t['path'], t['threshold']))

    def __is_match_loading(self, frame):
        """
        渡されたフレームが「ロード中」のフレームであるかを判定します.
        """
        # ロード中は、画面右下にロード中を示すアイコンが表示される.
        # そのため、右側の方を除いた範囲（だいたい左から80%）がブラックアウト
        # しているかどうかでロード中かを判定する.
        h, w = frame.shape[:2]
        w = int(w * 0.8) # 80%
        return np.all(frame[0:h, 0:w, :] == 0)

    def analyze(self, frame):
        # テンプレート画像を 1280x720 をベースに作成してしまったので、frame が
        # 1280x720 以外の解像度の場合、そのままだとテンプレートマッチが上手く
        # 動作しない。そのため、frame のサイズを 1280x720 に変更して対応する.
        if frame.shape[:2] != TEMPLATE_RESOLUTION:
            frame = cv2.resize(frame,
                dsize=(TEMPLATE_RESOLUTION[1], TEMPLATE_RESOLUTION[0]))

        if self.__is_match_loading(frame):
            return 'Loading'

        gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        for temp in self.templates:
            if temp.is_match(gray_frame):
                return temp.event
        return ''

