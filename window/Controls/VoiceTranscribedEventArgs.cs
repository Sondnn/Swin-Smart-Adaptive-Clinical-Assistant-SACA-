using System;

namespace SACA.WindowsApp.Controls
{
    public class VoiceTranscribedEventArgs : EventArgs
    {
        public VoiceTranscribedEventArgs(int questionId, string transcript, string recordingPath, string parsedResponseJson)
        {
            QuestionId = questionId;
            Transcript = transcript;
            RecordingPath = recordingPath;
            ParsedResponseJson = parsedResponseJson;
        }

        public int QuestionId { get; }
        public string Transcript { get; }
        public string RecordingPath { get; }
        public string ParsedResponseJson { get; }
    }
}
