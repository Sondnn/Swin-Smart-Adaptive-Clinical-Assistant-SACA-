using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Windows;
using System.Windows.Controls;
using System.Windows.Data;
using System.Windows.Documents;
using System.Windows.Input;
using System.Windows.Media;
using System.Windows.Media.Imaging;
using System.Windows.Navigation;
using System.Windows.Shapes;
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
        private string _recordedAge = "";

        public PatientInfoPage(MainWindow mainWindow)
        {
            InitializeComponent();
            _mainWindow = mainWindow;
            GenderVoiceRecorder.Configure(GetSpeechToTextLanguageCode);
            AgeVoiceRecorder.Configure(GetSpeechToTextLanguageCode);
            GenderVoiceRecorder.TranscriptReceived += VoiceRecorder_TranscriptReceived;
            AgeVoiceRecorder.TranscriptReceived += VoiceRecorder_TranscriptReceived;
        }

        private void GenderComboBox_SelectionChanged(object sender, SelectionChangedEventArgs e)
        {
            var gender = GetComboBoxValue(GenderComboBox);
            bool isFemale = gender == "Female";

            //PregnancyLabel.Visibility = isFemale ? Visibility.Visible : Visibility.Collapsed;
            //PregnancyComboBox.Visibility = isFemale ? Visibility.Visible : Visibility.Collapsed;
        }

        private void Back_Click(object sender, RoutedEventArgs e)
        {
            _mainWindow.NavigateToStart();
        }

        private void Continue_Click(object sender, RoutedEventArgs e)
        {
            string gender = GetComboBoxValue(GenderComboBox);
            string age = GetComboBoxValue(AgeComboBox);

            if (string.IsNullOrWhiteSpace(gender))
            {
                gender = _recordedGender;
            }

            if (string.IsNullOrWhiteSpace(age))
            {
                age = _recordedAge;
            }

            if (string.IsNullOrWhiteSpace(gender) || string.IsNullOrWhiteSpace(age))
            {
                MessageBox.Show("Please select gender and age group, or answer both using voice.");
                return;
            }

            _mainWindow.CurrentRequest.Gender = gender;
            //_mainWindow.CurrentRequest.PregnancyStatus = GetComboBoxValue(PregnancyComboBox);
            _mainWindow.CurrentRequest.AgeGroup = age;

            _mainWindow.NavigateToSymptoms();
        }

        private void VoiceRecorder_TranscriptReceived(object? sender, Controls.VoiceTranscribedEventArgs e)
        {
            string parsedValue = ParsedResponseReader.ReadSingleValue(e.ParsedResponseJson);

            if (e.QuestionId == 1)
            {
                _recordedGender = MapGenderResponse(parsedValue);
                SelectComboBoxValue(GenderComboBox, _recordedGender);
            }
            else if (e.QuestionId == 2)
            {
                _recordedAge = parsedValue;
                SelectComboBoxValue(AgeComboBox, parsedValue);
            }

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

        private string GetComboBoxValue(ComboBox comboBox)
        {
            if (comboBox.SelectedItem is ComboBoxItem item)
            {
                return item.Content?.ToString() ?? "";
            }

            return "";
        }

        private static void SelectComboBoxValue(ComboBox comboBox, string value)
        {
            foreach (ComboBoxItem item in comboBox.Items)
            {
                string itemValue = item.Content?.ToString() ?? "";

                if (itemValue.Equals(value, StringComparison.OrdinalIgnoreCase)
                    || itemValue.Contains(value, StringComparison.OrdinalIgnoreCase)
                    || value.Contains(itemValue, StringComparison.OrdinalIgnoreCase))
                {
                    comboBox.SelectedItem = item;
                    return;
                }
            }
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
