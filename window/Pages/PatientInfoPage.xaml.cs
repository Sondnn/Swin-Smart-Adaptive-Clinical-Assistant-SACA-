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

namespace SACA.WindowsApp.Pages
{
    /// <summary>
    /// Interaction logic for PatientInfoPage.xaml
    /// </summary>

    public partial class PatientInfoPage : UserControl
    {
        private readonly MainWindow _mainWindow;

        public PatientInfoPage(MainWindow mainWindow)
        {
            InitializeComponent();
            _mainWindow = mainWindow;
            VoiceRecorder.Configure(GetSpeechToTextLanguageCode);
            VoiceRecorder.TranscriptReceived += VoiceRecorder_TranscriptReceived;
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

            if (string.IsNullOrWhiteSpace(gender) || string.IsNullOrWhiteSpace(age))
            {
                MessageBox.Show("Please select gender and age group.");
                return;
            }

            _mainWindow.CurrentRequest.Gender = gender;
            //_mainWindow.CurrentRequest.PregnancyStatus = GetComboBoxValue(PregnancyComboBox);
            _mainWindow.CurrentRequest.AgeGroup = age;

            _mainWindow.NavigateToSymptoms();
        }

        private void VoiceRecorder_TranscriptReceived(object? sender, Controls.VoiceTranscribedEventArgs e)
        {
            _mainWindow.CurrentRequest.AudioRecordingPath = e.RecordingPath;
            _mainWindow.CurrentRequest.AudioRecordingPaths.Add(e.RecordingPath);
            _mainWindow.CurrentRequest.VoiceTranscripts.Add($"Patient details: {e.Transcript}");
        }

        private int GetSpeechToTextLanguageCode()
        {
            return _mainWindow.CurrentRequest.Language.Equals("English", StringComparison.OrdinalIgnoreCase)
                ? 1
                : 2;
        }

        private string GetComboBoxValue(ComboBox comboBox)
        {
            if (comboBox.SelectedItem is ComboBoxItem item)
            {
                return item.Content?.ToString() ?? "";
            }

            return "";
        }
    }
}
