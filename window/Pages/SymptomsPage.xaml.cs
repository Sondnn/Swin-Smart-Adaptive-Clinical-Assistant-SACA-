using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Runtime.InteropServices;
using System.Text;
using System.Threading.Tasks;
using System.Windows;
using System.Windows.Controls;
using System.Windows.Input;
using System.Windows.Media;
using SACA.WindowsApp.Services;

namespace SACA.WindowsApp.Pages
{
    /// <summary>
    /// Interaction logic for SymptomsPage.xaml
    /// </summary>
    public partial class SymptomsPage : UserControl
    {
        private readonly MainWindow _mainWindow;
        private readonly TriageApiService _triageApiService = new();
        private const string RecordingAlias = "triageRecording";
        private bool _isRecording;
        private bool _isTranscribing;
        private string _recordingPath = "";

        [DllImport("winmm.dll", CharSet = CharSet.Auto)]
        private static extern int mciSendString(string command, StringBuilder? returnValue, int returnLength, IntPtr winHandle);

        public SymptomsPage(MainWindow mainWindow)
        {
            InitializeComponent();
            _mainWindow = mainWindow;
        }

        private void Back_Click(object sender, RoutedEventArgs e)
        {
            _mainWindow.NavigateToPatientInfo();
        }

        private void Continue_Click(object sender, RoutedEventArgs e)
        {
            var symptoms = GetSelectedSymptoms();
            string severity = GetComboBoxValue(SeverityComboBox);

            if (!symptoms.Any() || string.IsNullOrWhiteSpace(severity))
            {
                MessageBox.Show("Please select at least one symptom and severity level.");
                return;
            }

            _mainWindow.CurrentRequest.Symptoms = symptoms;
            _mainWindow.CurrentRequest.Severity = severity;
            _mainWindow.CurrentRequest.Description = DescriptionTextBox.Text.Trim();
            _mainWindow.CurrentRequest.AudioRecordingPath = _recordingPath;

            _mainWindow.NavigateToDuration();
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
                int languageCode = GetSpeechToTextLanguageCode();
                string transcript = await _triageApiService.ConvertSpeechToTextAsync(audioFilePath, languageCode);

                if (string.IsNullOrWhiteSpace(transcript))
                {
                    RecordingStatusTextBlock.Text = "No speech text returned";
                    return;
                }

                DescriptionTextBox.Text = transcript.Trim();
                RecordingStatusTextBlock.Text = "Text added. Check it or record again.";
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

        private int GetSpeechToTextLanguageCode()
        {
            return _mainWindow.CurrentRequest.Language.Equals("English", StringComparison.OrdinalIgnoreCase)
                ? 1
                : 2;
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

        private List<string> GetSelectedSymptoms()
        {
            var symptoms = new List<string>();

            foreach (var checkBox in FindVisualChildren<CheckBox>(this))
            {
                if (checkBox.IsChecked == true && checkBox.Content != null)
                {
                    symptoms.Add(checkBox.Content.ToString() ?? "");
                }
            }

            return symptoms;
        }

        private string GetComboBoxValue(ComboBox comboBox)
        {
            if (comboBox.SelectedItem is ComboBoxItem item)
            {
                return item.Content?.ToString() ?? "";
            }

            return "";
        }

        private static IEnumerable<T> FindVisualChildren<T>(DependencyObject parent)
            where T : DependencyObject
        {
            if (parent == null)
            {
                yield break;
            }

            for (int i = 0; i < VisualTreeHelper.GetChildrenCount(parent); i++)
            {
                DependencyObject child = VisualTreeHelper.GetChild(parent, i);

                if (child is T typedChild)
                {
                    yield return typedChild;
                }

                foreach (T childOfChild in FindVisualChildren<T>(child))
                {
                    yield return childOfChild;
                }
            }
        }
    }
}
