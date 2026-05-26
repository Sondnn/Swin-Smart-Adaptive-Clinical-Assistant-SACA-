using System;
using System.Windows;
using System.Windows.Controls;
using SACA.WindowsApp.Services;

namespace SACA.WindowsApp.Pages
{
    /// <summary>
    /// Interaction logic for SickContactPage.xaml
    /// </summary>
    public partial class SickContactPage : UserControl
    {
        private readonly MainWindow _mainWindow;
        private string _recordedValue = "";

        public SickContactPage(MainWindow mainWindow)
        {
            InitializeComponent();
            _mainWindow = mainWindow;
            VoiceRecorder.Configure(GetSpeechToTextLanguageCode);
            VoiceRecorder.TranscriptReceived += VoiceRecorder_TranscriptReceived;

            if (!string.IsNullOrWhiteSpace(_mainWindow.CurrentRequest.RecentSickContact))
            {
                SelectRadioValue(_mainWindow.CurrentRequest.RecentSickContact);
            }
        }

        private void Back_Click(object sender, RoutedEventArgs e)
        {
            _mainWindow.NavigateToChronicConditions();
        }

        private void Assess_Click(object sender, RoutedEventArgs e)
        {
            string selectedValue = GetSelectedValue();

            if (string.IsNullOrWhiteSpace(selectedValue))
            {
                selectedValue = _recordedValue;
            }

            if (string.IsNullOrWhiteSpace(selectedValue))
            {
                MessageBox.Show("Please select whether you have been in contact with someone sick recently, or answer using voice.");
                return;
            }

            _mainWindow.CurrentRequest.RecentSickContact = selectedValue;
            _mainWindow.NavigateToLoading();
        }

        private void VoiceRecorder_TranscriptReceived(object? sender, Controls.VoiceTranscribedEventArgs e)
        {
            _recordedValue = ParsedResponseReader.ReadSingleValue(e.ParsedResponseJson);
            SelectRadioValue(_recordedValue);
            _mainWindow.CurrentRequest.AudioRecordingPath = e.RecordingPath;
            _mainWindow.CurrentRequest.AudioRecordingPaths.Add(e.RecordingPath);
            _mainWindow.CurrentRequest.VoiceTranscripts.Add($"Question {e.QuestionId}: {e.Transcript}");
        }

        private int GetSpeechToTextLanguageCode()
        {
            return _mainWindow.CurrentRequest.Language.Equals("English", StringComparison.OrdinalIgnoreCase)
                ? 1
                : 0;
        }

        private string GetSelectedValue()
        {
            if (YesRadioButton.IsChecked == true)
            {
                return "Yes";
            }

            if (NoRadioButton.IsChecked == true)
            {
                return "No";
            }

            if (UnknownRadioButton.IsChecked == true)
            {
                return "Unknown";
            }

            return "";
        }

        private void SelectRadioValue(string value)
        {
            string normalisedValue = value.Trim();

            YesRadioButton.IsChecked = normalisedValue == "1"
                || normalisedValue.Contains("yes", StringComparison.OrdinalIgnoreCase)
                || normalisedValue.Contains("yuwa", StringComparison.OrdinalIgnoreCase);
            NoRadioButton.IsChecked = normalisedValue == "0"
                || normalisedValue.Equals("No", StringComparison.OrdinalIgnoreCase)
                || normalisedValue.Contains("wiya", StringComparison.OrdinalIgnoreCase);
            UnknownRadioButton.IsChecked = normalisedValue == "2"
                || normalisedValue.Contains("unknown", StringComparison.OrdinalIgnoreCase)
                || normalisedValue.Contains("not sure", StringComparison.OrdinalIgnoreCase)
                || normalisedValue.Contains("don't know", StringComparison.OrdinalIgnoreCase)
                || normalisedValue.Contains("kulini", StringComparison.OrdinalIgnoreCase);
        }
    }
}
