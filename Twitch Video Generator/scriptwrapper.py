import subprocess
import os
import math
import datetime
import pickle
import random
current_path = os.path.dirname(os.path.realpath(__file__))



def createTwitchVideoFromJSON(videojson):
    print(videojson)
    final_clips = []

    clips = videojson["clips"]
    colour1 = videojson["colour1"]
    colour2 = videojson["colour2"]
    background_volume = videojson["background_volume"]
    audio_cat = videojson["music"]


    for clip in clips:
        print(clip)
        id = clip["id"]
        start_cut = clip["start_cut"]
        end_cut = clip["end_cut"]
        audio = clip["audio"]
        used = clip["keep"]

        isUpload = clip["isUpload"]
        isIntro = clip["isIntro"]
        isInterval = clip["isInterval"]
        uploadMp4 = clip["mp4"]
        uploadDuration = clip["duration"]
        streamer_name = clip["streamer_name"]
        title = clip["title"]
        channel_url = clip["channel_url"]



        wrapper = TwitchClipWrapper(id, streamer_name, title, channel_url)
        wrapper.mp4 = uploadMp4
        wrapper.vid_duration = uploadDuration
        wrapper.isUpload = isUpload
        wrapper.isInterval = isInterval
        wrapper.isIntro = isIntro
        wrapper.start_cut = start_cut
        wrapper.end_cut = end_cut
        wrapper.audio = audio
        wrapper.isUsed = used

        final_clips.append(wrapper)

    video = TwitchVideo(final_clips)
    video.colour1 = colour1
    video.colour2 = colour2
    video.audio_cat = audio_cat
    print(final_clips)
    video.background_volume = background_volume
    return video


def saveTwitchVideo(folderName, video):
    print(f'Temp/%s/vid.data' % folderName)
    with open(f'Temp/%s/vid.data' % folderName, 'wb') as pickle_file:
        pickle.dump(video, pickle_file)



class TwitchVideo():
    def __init__(self, clips):
        self.clips = clips
        self.colour1 = None
        self.colour2 = None
        self.background_volume = None
        self.audio_cat = None



class TwitchClipWrapper():
    def __init__(self, id, streamer_name, clip_title, channel_url):
        self.channel_url = channel_url
        self.id = id
        self.streamer_name = streamer_name
        self.audio = 1
        self.isUsed = False
        self.isInterval = False
        self.isUpload = False
        self.mp4 = "AndreasGreenLive-702952046"
        self.clip_name = clip_title
        self.isIntro = False
        # result = subprocess.run(["ffprobe", "-v", "error", "-show_entries",
        #              "format=duration", "-of",
        #              "default=noprint_wrappers=1:nokey=1", f"{current_path}\VideoFiles\AndreasGreenLive-702952046.mp4"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        self.vid_duration = None

        #Getting duration of video clips to trim a percentage of the beginning off
        self.start_cut = 0
        self.end_cut = 0




class ScriptWrapper():
    def __init__(self, script):
        self.rawScript = script
        self.scriptMap = []
        self.setupScriptMap()


    def addClipAtStart(self, clip):
        self.rawScript = [clip] + self.rawScript
        self.scriptMap = [True] + self.scriptMap


    def addScriptWrapper(self, scriptwrapper):
        self.rawScript = self.rawScript + scriptwrapper.rawScript
        self.scriptMap = self.scriptMap + scriptwrapper.scriptMap


    def moveDown(self, i):
        if i > 0:
            copy1 = self.scriptMap[i-1]
            copy2 = self.rawScript[i-1]

            self.scriptMap[i-1] = self.scriptMap[i]
            self.rawScript[i-1] = self.rawScript[i]

            self.scriptMap[i] = copy1
            self.rawScript[i] = copy2
        else:
            print("already at bottom!")

    def moveUp(self, i):
        if i < len(self.scriptMap) - 1:
            copy1 = self.scriptMap[i+1]
            copy2 = self.rawScript[i+1]

            self.scriptMap[i+1] = self.scriptMap[i]
            self.rawScript[i+1] = self.rawScript[i]

            self.scriptMap[i] = copy1
            self.rawScript[i] = copy2
        else:
            print("already at top!")

    def setupScriptMap(self):
        for mainComment in self.rawScript:
            line = False
            self.scriptMap.append(line)


    def keep(self, mainCommentIndex):
        self.scriptMap[mainCommentIndex] = True

    def skip(self, mainCommentIndex):
        self.scriptMap[mainCommentIndex] = False

    def setCommentStart(self, x, start):
        self.rawScript[x].start_cut = start

    def setCommentEnd(self, x, end):
        self.rawScript[x].end_cut = end

    def getCommentData(self, x, y):
        return self.rawScript[x][y]

    def getCommentAmount(self):
        return len(self.scriptMap)

    def getEditedCommentThreadsAmount(self):
        return len([commentThread for commentThread in self.scriptMap if commentThread[0] is True])

    def getEditedCommentAmount(self):
        commentThreads = ([commentThread for commentThread in self.scriptMap])
        count = 0
        for commentThread in commentThreads:
            for comment in commentThread:
                if comment is True:
                    count += 1
        return count

    def getEditedWordCount(self):
        commentThreads = ([commentThread for commentThread in self.scriptMap])
        word_count = 0
        for x, commentThread in enumerate(commentThreads):
            for y, comment in enumerate(commentThread):
                if comment is True:
                    word_count += len(self.rawScript[x][y].text.split(" "))
        return word_count

    def getEditedCharacterCount(self):
        commentThreads = ([commentThread for commentThread in self.scriptMap])
        word_count = 0
        for x, commentThread in enumerate(commentThreads):
            for y, comment in enumerate(commentThread):
                if comment is True:
                    word_count += len(self.rawScript[x][y].text)
        return word_count


    def getCommentInformation(self, x):
        return self.rawScript[x]


    def getKeptClips(self):
        final_script = []
        for i, clip in enumerate(self.scriptMap):
            if clip:
                final_script.append(self.rawScript[i])
        return final_script

    def getEstimatedVideoTime(self):
        time = 0
        for i, comment in enumerate(self.scriptMap):
            if comment is True:
                time += round(self.rawScript[i].vid_duration - (self.rawScript[i].start_cut / 1000) - (self.rawScript[i].end_cut / 1000), 1)
        obj = datetime.timedelta(seconds=math.ceil(time))
        return  obj

