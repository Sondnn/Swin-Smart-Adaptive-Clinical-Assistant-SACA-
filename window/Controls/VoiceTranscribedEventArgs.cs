using System;

namespace SACA.WindowsApp.Controls
{
    public class VoiceTranscribedEventArgs : EventArgs
    {
        public VoiceTranscribedEventArgs(string transcript, string recordingPath)
        {
            Transcript = transcript;
            RecordingPath = recordingPath;
        }

        public string Transcript { get; }
        public string RecordingPath { get; }
    }
}
