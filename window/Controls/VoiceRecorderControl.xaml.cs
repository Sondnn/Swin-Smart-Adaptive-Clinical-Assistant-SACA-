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

        public static readonly DependencyProperty QuestionIdProperty = DependencyProperty.Register(
            nameof(QuestionId),
            typeof(int),
            typeof(VoiceRecorderControl),
            new PropertyMetadata(0));

        public static readonly DependencyProperty LabelProperty = DependencyProperty.Register(
            nameof(Label),
            typeof(string),
            typeof(VoiceRecorderControl),
            new PropertyMetadata("Voice Recording", OnLabelChanged));

        public int QuestionId
        {
            get => (int)GetValue(QuestionIdProperty);
            set => SetValue(QuestionIdProperty, value);
        }

        public string Label
        {
            get => (string)GetValue(LabelProperty);
            set => SetValue(LabelProperty, value);
        }

        [DllImport("winmm.dll", CharSet = CharSet.Auto)]
        private static extern int mciSendString(string command, StringBuilder? returnValue, int returnLength, IntPtr winHandle);

        public VoiceRecorderControl()
        {
            InitializeComponent();
            TitleTextBlock.Text = Label;
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
                RecordingStatusTextBlock.Text = AppLanguage.T("recording");
            }
            catch (Exception ex)
            {
                _isRecording = false;
                RecordingStatusTextBlock.Text = AppLanguage.T("voice_failed");
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
                RecordingStatusTextBlock.Text = Path.GetFileName(_recordingPath);
            }
            catch (Exception ex)
            {
                _recordingPath = "";
                RecordingStatusTextBlock.Text = AppLanguage.T("voice_failed");
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
            if (QuestionId <= 0)
            {
                RecordingStatusTextBlock.Text = "Question is not configured";
                MessageBox.Show("This voice recorder does not have a question ID configured.");
                return;
            }

            _isTranscribing = true;
            RecordButton.IsEnabled = false;
            RecordingStatusTextBlock.Text = AppLanguage.T("processing_voice");

            try
            {
                SpeechToTextPageResult result = await _triageApiService.ConvertSpeechToTextPageAsync(audioFilePath, _getLanguageCode(), QuestionId);

                if (string.IsNullOrWhiteSpace(result.DisplayText))
                {
                    RecordingStatusTextBlock.Text = AppLanguage.T("voice_failed");
                    return;
                }

                RecordingStatusTextBlock.Text = $"{AppLanguage.T("accepted")}: {result.DisplayText}";
                TranscriptReceived?.Invoke(
                    this,
                    new VoiceTranscribedEventArgs(result.QuestionId, result.DisplayText, audioFilePath, result.ParsedResponseJson));
            }
            catch (Exception ex)
            {
                RecordingStatusTextBlock.Text = AppLanguage.T("voice_failed");
                MessageBox.Show($"Could not process the voice answer: {ex.Message}");
            }
            finally
            {
                _isTranscribing = false;
                RecordButton.IsEnabled = true;
            }
        }

        private static void OnLabelChanged(DependencyObject dependencyObject, DependencyPropertyChangedEventArgs e)
        {
            if (dependencyObject is VoiceRecorderControl control && control.TitleTextBlock != null)
            {
                control.TitleTextBlock.Text = e.NewValue?.ToString() ?? "Voice Recording";
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
