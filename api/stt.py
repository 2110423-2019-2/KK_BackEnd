from google.cloud import speech_v1
from google.cloud.speech_v1 import enums
import io
import sys
import os
os.environ["GOOGLE_APPLICATION_CREDENTIALS"]=os.getcwd()+"/api/speech_auth.json"
import urllib.request
from pydub import AudioSegment

def checkDir():
    path = os.path.abspath("./user_speech/")
    if not os.path.exists(path):
        os.makedirs(path)

def convert(abs_file_path):
    sound = AudioSegment.from_file(abs_file_path)
    sound = sound.set_channels(1)
    sound = sound.set_sample_width(2)
    sound = sound.set_frame_rate(48000)

    abs_out_file_path = abs_file_path[:-4] + ".wav"

    sound.export(abs_out_file_path, format="wav")

    return abs_out_file_path

def sample_recognize(url, username):
    checkDir()
    """
    Transcribe a short audio file using synchronous speech recognition

    Args:
      local_file_path Path to local audio file, e.g. /path/audio.wav
    """

    # for testing #
    '''
    url = "https://stupidz.s3-ap-southeast-1.amazonaws.com/nicotineN.wav"
    local_file_path = "C:\\Users\\non_s\\Desktop\\nonnon.wav" '''
    ##########################
    local_file_path = os.path.abspath("./user_speech/"+username+"_temp.weba")

    urllib.request.urlretrieve(url, local_file_path)
    local_file_path = convert(local_file_path)
    client = speech_v1.SpeechClient()

    # The language of the supplied audio
    language_code = "th-TH"
    # Sample rate in Hertz of the audio data sent
    sample_rate_hertz = 48000
    # Encoding of audio data sent. This sample sets this explicitly.
    # This field is optional for FLAC and WAV audio formats.
    encoding = enums.RecognitionConfig.AudioEncoding.LINEAR16
    config = {
        "language_code": language_code,
        "sample_rate_hertz": sample_rate_hertz,
        "encoding": encoding,
    }
    with io.open(local_file_path, "rb") as f:
        content = f.read()
    audio = {"content": content}
    response = client.recognize(config, audio)
    out = ""
    for result in response.results:
        # First alternative is the most probable result
        alternative = result.alternatives[0]
        # print(u"{}".format(alternative.transcript))
        out += u"{}".format(alternative.transcript)
    return out



# Download the file from `url`, save it in a temporary directory and get the
# path to it (e.g. '/tmp/tmpb48zma.txt') in the `file_name` variable:

if __name__ == '__main__':
    url = sys.argv[1]
    path = sys.argv[2]
    sample_recognize(url,path)
