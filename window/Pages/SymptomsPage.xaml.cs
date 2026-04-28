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
    /// Interaction logic for SymptomsPage.xaml
    /// </summary>
    public partial class SymptomsPage : UserControl
    {
        private readonly MainWindow _mainWindow;

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

            _mainWindow.NavigateToDuration();
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
