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

            if (!string.IsNullOrWhiteSpace(_mainWindow.CurrentRequest.Duration))
            {
                SelectRadioValue(_mainWindow.CurrentRequest.Duration);
            }
        }

        private void Back_Click(object sender, RoutedEventArgs e)
        {
            _mainWindow.NavigateToSeverity();
        }

        private void Continue_Click(object sender, RoutedEventArgs e)
        {
            string duration = GetSelectedValue();

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
            SelectRadioValue(_recordedDuration);
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
            if (LessThanDayRadioButton.IsChecked == true)
            {
                return LessThanDayRadioButton.Tag?.ToString() ?? "";
            }

            if (MoreThanDayRadioButton.IsChecked == true)
            {
                return MoreThanDayRadioButton.Tag?.ToString() ?? "";
            }

            if (UnknownRadioButton.IsChecked == true)
            {
                return UnknownRadioButton.Tag?.ToString() ?? "";
            }

            return "";
        }

        private void SelectRadioValue(string value)
        {
            LessThanDayRadioButton.IsChecked = MatchesDuration(value, "Less than a day") || value.Contains("less", StringComparison.OrdinalIgnoreCase);
            MoreThanDayRadioButton.IsChecked = MatchesDuration(value, "More than a day") || value.Contains("more", StringComparison.OrdinalIgnoreCase);
            UnknownRadioButton.IsChecked = value.Contains("unknown", StringComparison.OrdinalIgnoreCase);
        }

        private static bool MatchesDuration(string value, string option)
        {
            return value.Equals(option, StringComparison.OrdinalIgnoreCase)
                || value.Contains(option, StringComparison.OrdinalIgnoreCase)
                || option.Contains(value, StringComparison.OrdinalIgnoreCase);
        }
    }
}
