using System;
using System.Collections.Generic;
using System.Linq;
using System.Windows;
using System.Windows.Controls;
using System.Windows.Media;
using SACA.WindowsApp.Services;

namespace SACA.WindowsApp.Pages
{
    /// <summary>
    /// Interaction logic for ChronicConditionsPage.xaml
    /// </summary>
    public partial class ChronicConditionsPage : UserControl
    {
        private readonly MainWindow _mainWindow;
        private List<string> _recordedConditions = new();

        public ChronicConditionsPage(MainWindow mainWindow)
        {
            InitializeComponent();
            _mainWindow = mainWindow;
            VoiceRecorder.Configure(GetSpeechToTextLanguageCode);
            VoiceRecorder.TranscriptReceived += VoiceRecorder_TranscriptReceived;
        }

        private void Back_Click(object sender, RoutedEventArgs e)
        {
            _mainWindow.NavigateToSymptomsHistory();
        }

        private void Continue_Click(object sender, RoutedEventArgs e)
        {
            List<string> selectedConditions = GetSelectedConditions();

            if (!selectedConditions.Any())
            {
                selectedConditions = _recordedConditions;
            }

            if (!selectedConditions.Any())
            {
                MessageBox.Show("Please select any chronic conditions, choose Unknown / None, or answer using voice.");
                return;
            }

            _mainWindow.CurrentRequest.ChronicConditions = selectedConditions;
            _mainWindow.NavigateToSickContact();
        }

        private void VoiceRecorder_TranscriptReceived(object? sender, Controls.VoiceTranscribedEventArgs e)
        {
            _recordedConditions = ParsedResponseReader.ReadStringList(e.ParsedResponseJson);
            SelectCheckBoxes(_recordedConditions);
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

        private void UnknownCheckBox_Checked(object sender, RoutedEventArgs e)
        {
            foreach (CheckBox checkBox in FindVisualChildren<CheckBox>(this))
            {
                if (checkBox != UnknownCheckBox)
                {
                    checkBox.IsChecked = false;
                }
            }
        }

        private void ConditionCheckBox_Checked(object sender, RoutedEventArgs e)
        {
            if (sender != UnknownCheckBox)
            {
                UnknownCheckBox.IsChecked = false;
            }
        }

        private List<string> GetSelectedConditions()
        {
            var conditions = new List<string>();

            foreach (CheckBox checkBox in FindVisualChildren<CheckBox>(this))
            {
                if (checkBox.IsChecked == true && checkBox.Content != null)
                {
                    conditions.Add(checkBox.Tag?.ToString() ?? checkBox.Content.ToString() ?? "");
                }
            }

            return conditions;
        }

        private void SelectCheckBoxes(IEnumerable<string> values)
        {
            foreach (CheckBox checkBox in FindVisualChildren<CheckBox>(this))
            {
                string checkBoxValue = checkBox.Content?.ToString() ?? "";
                string tagValue = checkBox.Tag?.ToString() ?? "";
                checkBox.IsChecked = values.Any(value =>
                    checkBoxValue.Equals(value, StringComparison.OrdinalIgnoreCase)
                    || tagValue.Equals(value, StringComparison.OrdinalIgnoreCase)
                    || checkBoxValue.Contains(value, StringComparison.OrdinalIgnoreCase)
                    || tagValue.Contains(value, StringComparison.OrdinalIgnoreCase)
                    || value.Contains(checkBoxValue, StringComparison.OrdinalIgnoreCase));
            }
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
