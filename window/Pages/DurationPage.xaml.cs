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
    /// Interaction logic for DurationPage.xaml
    /// </summary>

    public partial class DurationPage : UserControl
    {
        private readonly MainWindow _mainWindow;
        private string _recordedDuration = "";

        public DurationPage(MainWindow mainWindow)
        {
            InitializeComponent();
            _mainWindow = mainWindow;
            VoiceRecorder.Configure(GetSpeechToTextLanguageCode);
            VoiceRecorder.TranscriptReceived += VoiceRecorder_TranscriptReceived;
        }

        private void Back_Click(object sender, RoutedEventArgs e)
        {
            _mainWindow.NavigateToSymptoms();
        }

        private void Continue_Click(object sender, RoutedEventArgs e)
        {
            string duration = GetComboBoxValue(DurationComboBox);

            if (string.IsNullOrWhiteSpace(duration))
            {
                duration = _recordedDuration;
            }

            if (string.IsNullOrWhiteSpace(duration))
            {
                MessageBox.Show("Please select symptom duration, or answer using voice.");
                return;
            }

            _mainWindow.CurrentRequest.Duration = duration;
            _mainWindow.NavigateToSymptomsHistory();
        }

        private void VoiceRecorder_TranscriptReceived(object? sender, Controls.VoiceTranscribedEventArgs e)
        {
            _recordedDuration = ParsedResponseReader.ReadSingleValue(e.ParsedResponseJson);
            SelectComboBoxValue(DurationComboBox, _recordedDuration);
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
    }
}
