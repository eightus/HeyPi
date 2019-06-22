import threading
import wave
import os

import pyaudio
import speech_recognition as sr


class Record:

    def __init__(self, conn, action):

        self.r = sr.Recognizer()
        self.check = False
        self.conn = conn
        self.action = action
        print('Started')

    def start_record(self):
        self.check = True
        thread = threading.Thread(target=self.record)
        thread.start()

    def stop_record(self):
        self.check = False

    def record(self):
        dir_path = os.path.dirname(os.path.realpath(__file__))
        chunk = 512  # Record in chunks of 512 samples
        sample_format = pyaudio.paInt16  # 16 bits per sample
        channels = 1
        fs = 44100  # Record at 44100 samples per second
        filename = dir_path + "/output.wav"

        p = pyaudio.PyAudio()  # Create an interface to PortAudio

        print('Recording')

        stream = p.open(format=sample_format,
                        channels=channels,
                        rate=fs,
                        frames_per_buffer=chunk,
                        input=True)

        frames = []  # Initialize array to store frames

        # Store data in chunks for 3 seconds
        while self.check is True:
            data = stream.read(chunk, exception_on_overflow=False)
            frames.append(data)

        # Stop and close the stream
        stream.stop_stream()
        stream.close()
        # Terminate the PortAudio interface
        p.terminate()

        # Save the recorded data as a WAV file
        wf = wave.open(filename, 'wb')
        wf.setnchannels(channels)
        wf.setsampwidth(p.get_sample_size(sample_format))
        wf.setframerate(fs)
        wf.writeframes(b''.join(frames))
        wf.close()

        print('Finished recording')
        self.process_record(dir_path + '/output.wav')

    def process_record(self, input_file):
        file = sr.AudioFile(input_file)
        with file as source:
            audio = self.r.record(source)

        try:
            output = self.r.recognize_google(audio, language='en-GB')
            print(output)
            status = 'True'
            if self.action.check_condition(output.lower()) is False:
                status = 'False'
                self.action.reply_dont_understand()
            self.conn.insert_chat_log(output.lower(), status)

        except sr.UnknownValueError:
            output = 'Error: Could Not Understand'
            print(output)
            status = 'False'
            self.conn.insert_chat_log(output.lower(), status)
            self.action.reply_dont_understand()

        except sr.RequestError:
            output = 'Error: Google not available'
            print(output)
            status = 'False'
            self.conn.insert_chat_log(output.lower(), status)
            self.action.reply_not_available()


#  Test Code
p = pyaudio.PyAudio()
for i in range(p.get_device_count()):
    dev = p.get_device_info_by_index(i)
    print((i, dev['name'], dev['maxInputChannels']))
