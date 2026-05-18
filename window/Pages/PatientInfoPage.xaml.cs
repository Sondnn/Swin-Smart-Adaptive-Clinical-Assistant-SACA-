using System;
using System.Windows;
using System.Windows.Controls;
using SACA.WindowsApp.Services;

namespace SACA.WindowsApp.Pages
{
    /// <summary>
    /// Interaction logic for PatientInfoPage.xaml
    /// </summary>
    public partial class PatientInfoPage : UserControl
    {
        private readonly MainWindow _mainWindow;
        private string _recordedGender = "";

        public PatientInfoPage(MainWindow mainWindow)
        {
            InitializeComponent();
            _mainWindow = mainWindow;
            GenderVoiceRecorder.Configure(GetSpeechToTextLanguageCode);
            GenderVoiceRecorder.TranscriptReceived += VoiceRecorder_TranscriptReceived;

            if (!string.IsNullOrWhiteSpace(_mainWindow.CurrentRequest.Gender))
            {
                SelectRadioValue(_mainWindow.CurrentRequest.Gender);
            }
        }

        private void Back_Click(object sender, RoutedEventArgs e)
        {
            _mainWindow.NavigateToStart();
        }

        private void Continue_Click(object sender, RoutedEventArgs e)
        {
            string gender = GetSelectedValue();

            if (string.IsNullOrWhiteSpace(gender))
            {
                gender = _recordedGender;
            }

            if (string.IsNullOrWhiteSpace(gender))
            {
                MessageBox.Show("Please select gender, or answer using voice.");
                return;
            }

            _mainWindow.CurrentRequest.Gender = gender;
            _mainWindow.NavigateToAge();
        }

        private void VoiceRecorder_TranscriptReceived(object? sender, Controls.VoiceTranscribedEventArgs e)
        {
            _recordedGender = MapGenderResponse(ParsedResponseReader.ReadSingleValue(e.ParsedResponseJson));
            SelectRadioValue(_recordedGender);
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
            if (MaleRadioButton.IsChecked == true)
            {
                return MaleRadioButton.Tag?.ToString() ?? "";
            }

            if (FemaleRadioButton.IsChecked == true)
            {
                return FemaleRadioButton.Tag?.ToString() ?? "";
            }

            if (UnknownRadioButton.IsChecked == true)
            {
                return UnknownRadioButton.Tag?.ToString() ?? "";
            }

            return "";
        }

        private void SelectRadioValue(string value)
        {
            string normalisedValue = value.Trim();

            MaleRadioButton.IsChecked = normalisedValue.Equals("Male", StringComparison.OrdinalIgnoreCase);
            FemaleRadioButton.IsChecked = normalisedValue.Equals("Female", StringComparison.OrdinalIgnoreCase);
            UnknownRadioButton.IsChecked = normalisedValue.Contains("unknown", StringComparison.OrdinalIgnoreCase)
                || normalisedValue.Contains("prefer", StringComparison.OrdinalIgnoreCase);
        }

        private static string MapGenderResponse(string value)
        {
            return value.Trim() switch
            {
                "0" => "Female",
                "1" => "Male",
                "2" => "Unknown / Prefer not to say",
                _ => value
            };
        }
    }
}
