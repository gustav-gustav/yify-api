import os, glob


class Resub:
    def __init__(self):
        try:
            os.chdir(os.getcwd())
            self.srt = self.globber('srt')
            self.movie = self.globber('mp4') + self.globber('mkv')
            if self.movie:
                self.rename()
            else:
                print("No movie found")
        except Exception as e:
            print(e)

    def globber(self, ext):
        #glob_path = os.path.join(self.path, f'*.{ext}')
        glob_list = glob.glob(f'*.{ext}')
        if glob_list:
            return glob_list[0]
        return ''

    def rename(self):
        movie_name = os.path.splitext(self.movie)[0]
        renamed = f'{movie_name}.srt'
        os.rename(self.srt, renamed)
        print(f'Renamed {self.srt} to {renamed}')


if __name__ == '__main__':
    Resub()
