using System;
using System.Windows;
using System.Windows.Controls;

namespace SACA.WindowsApp.Pages
{
    /// <summary>
    /// Interaction logic for SickContactPage.xaml
    /// </summary>
    public partial class SickContactPage : UserControl
    {
        private readonly MainWindow _mainWindow;

        public SickContactPage(MainWindow mainWindow)
        {
            InitializeComponent();
            _mainWindow = mainWindow;
            VoiceRecorder.Configure(GetSpeechToTextLanguageCode);
            VoiceRecorder.TranscriptReceived += VoiceRecorder_TranscriptReceived;
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
                MessageBox.Show("Please select whether you have been in contact with someone sick recently.");
                return;
            }

            _mainWindow.CurrentRequest.RecentSickContact = selectedValue;
            _mainWindow.NavigateToLoading();
        }

        private void VoiceRecorder_TranscriptReceived(object? sender, Controls.VoiceTranscribedEventArgs e)
        {
            _mainWindow.CurrentRequest.AudioRecordingPath = e.RecordingPath;
            _mainWindow.CurrentRequest.AudioRecordingPaths.Add(e.RecordingPath);
            _mainWindow.CurrentRequest.VoiceTranscripts.Add($"Sick contact: {e.Transcript}");
        }

        private int GetSpeechToTextLanguageCode()
        {
            return _mainWindow.CurrentRequest.Language.Equals("English", StringComparison.OrdinalIgnoreCase)
                ? 1
                : 2;
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
    }
}
