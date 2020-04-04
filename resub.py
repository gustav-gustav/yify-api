import os, glob


class Resub:
    '''Looks for .srt files and renames them after finding a .mp4 or .mkv file in your current dirctory.'''
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
        '''Gets the filename for a given extension. Expects to find only one file of that extension'''
        glob_list = glob.glob(f'*.{ext}')
        if glob_list:
            return glob_list[0]
        return ''

    def rename(self):
        '''Renames the .srt file to the movie name'''
        movie_name = os.path.splitext(self.movie)[0]
        renamed = f'{movie_name}.srt'
        os.rename(self.srt, renamed)
        print(f'Renamed {self.srt} to {renamed}')


if __name__ == '__main__':
    Resub()
