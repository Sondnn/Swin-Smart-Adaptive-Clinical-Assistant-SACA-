using System;
using System.IO;
using System.Runtime.InteropServices;
using System.Text;
using System.Threading.Tasks;
using System.Windows;
using System.Windows.Controls;
using System.Windows.Input;
using SACA.WindowsApp.Services;

namespace SACA.WindowsApp.Controls
{
    /// <summary>
    /// Shared hold-to-record control that saves a WAV file and sends it to speech-to-text.
    /// </summary>
    public partial class VoiceRecorderControl : UserControl
    {
        private readonly TriageApiService _triageApiService = new();
        private const string RecordingAlias = "triageRecording";
        private Func<int> _getLanguageCode = () => 1;
        private bool _isRecording;
        private bool _isTranscribing;
        private string _recordingPath = "";

        public event EventHandler<VoiceTranscribedEventArgs>? TranscriptReceived;

        public string LastRecordingPath => _recordingPath;

        [DllImport("winmm.dll", CharSet = CharSet.Auto)]
        private static extern int mciSendString(string command, StringBuilder? returnValue, int returnLength, IntPtr winHandle);

        public VoiceRecorderControl()
        {
            InitializeComponent();
        }

        public void Configure(Func<int> getLanguageCode)
        {
            _getLanguageCode = getLanguageCode;
        }

        private void RecordButton_PreviewMouseLeftButtonDown(object sender, MouseButtonEventArgs e)
        {
            StartRecording();
            RecordButton.CaptureMouse();
        }

        private async void RecordButton_PreviewMouseLeftButtonUp(object sender, MouseButtonEventArgs e)
        {
            string savedRecordingPath = StopRecording();

            if (!string.IsNullOrWhiteSpace(savedRecordingPath))
            {
                await ConvertRecordingToTextAsync(savedRecordingPath);
            }
        }

        private void RecordButton_MouseLeave(object sender, MouseEventArgs e)
        {
            if (_isRecording && Mouse.LeftButton != MouseButtonState.Pressed)
            {
                StopRecording();
            }
        }

        private void StartRecording()
        {
            if (_isRecording || _isTranscribing)
            {
                return;
            }

            try
            {
                string recordingsFolder = Path.Combine(
                    Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData),
                    "SACA",
                    "Recordings");

                Directory.CreateDirectory(recordingsFolder);
                _recordingPath = Path.Combine(recordingsFolder, $"triage-{DateTime.Now:yyyyMMdd-HHmmss}.wav");

                SendMciCommand($"open new Type waveaudio Alias {RecordingAlias}");
                SendMciCommand($"set {RecordingAlias} bitspersample 16 channels 1 samplespersec 16000 bytespersec 32000 alignment 2");
                SendMciCommand($"record {RecordingAlias}");

                _isRecording = true;
                RecordingStatusTextBlock.Text = "Recording... release to stop";
            }
            catch (Exception ex)
            {
                _isRecording = false;
                RecordingStatusTextBlock.Text = "Recording unavailable";
                MessageBox.Show($"Could not start voice recording: {ex.Message}");
                CloseRecordingDevice();
            }
        }

        private string StopRecording()
        {
            if (!_isRecording)
            {
                return "";
            }

            string savedRecordingPath = "";

            try
            {
                SendMciCommand($"stop {RecordingAlias}");
                SendMciCommand($"save {RecordingAlias} \"{_recordingPath}\"");
                savedRecordingPath = _recordingPath;
                RecordingStatusTextBlock.Text = $"Recording saved: {Path.GetFileName(_recordingPath)}";
            }
            catch (Exception ex)
            {
                _recordingPath = "";
                RecordingStatusTextBlock.Text = "Recording failed";
                MessageBox.Show($"Could not save voice recording: {ex.Message}");
            }
            finally
            {
                _isRecording = false;
                CloseRecordingDevice();
                RecordButton.ReleaseMouseCapture();
            }

            return savedRecordingPath;
        }

        private async Task ConvertRecordingToTextAsync(string audioFilePath)
        {
            _isTranscribing = true;
            RecordButton.IsEnabled = false;
            RecordingStatusTextBlock.Text = "Converting speech to text...";

            try
            {
                string transcript = await _triageApiService.ConvertSpeechToTextAsync(audioFilePath, _getLanguageCode());

                if (string.IsNullOrWhiteSpace(transcript))
                {
                    RecordingStatusTextBlock.Text = "No speech text returned";
                    return;
                }

                RecordingStatusTextBlock.Text = $"Text: {transcript.Trim()}";
                TranscriptReceived?.Invoke(this, new VoiceTranscribedEventArgs(transcript.Trim(), audioFilePath));
            }
            catch (Exception ex)
            {
                RecordingStatusTextBlock.Text = "Speech-to-text failed";
                MessageBox.Show($"Could not convert the recording to text: {ex.Message}");
            }
            finally
            {
                _isTranscribing = false;
                RecordButton.IsEnabled = true;
            }
        }

        private static void SendMciCommand(string command)
        {
            int result = mciSendString(command, null, 0, IntPtr.Zero);

            if (result != 0)
            {
                throw new InvalidOperationException($"Audio command failed: {command}");
            }
        }

        private static void CloseRecordingDevice()
        {
            mciSendString($"close {RecordingAlias}", null, 0, IntPtr.Zero);
        }
    }
}
