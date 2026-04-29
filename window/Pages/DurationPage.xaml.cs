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
    /// Interaction logic for DurationPage.xaml
    /// </summary>

    public partial class DurationPage : UserControl
    {
        private readonly MainWindow _mainWindow;

        public DurationPage(MainWindow mainWindow)
        {
            InitializeComponent();
            _mainWindow = mainWindow;
        }

        private void Back_Click(object sender, RoutedEventArgs e)
        {
            _mainWindow.NavigateToSymptoms();
        }

        private void Assess_Click(object sender, RoutedEventArgs e)
        {
            string duration = GetComboBoxValue(DurationComboBox);

            if (string.IsNullOrWhiteSpace(duration))
            {
                MessageBox.Show("Please select symptom duration.");
                return;
            }

            _mainWindow.CurrentRequest.Duration = duration;
            _mainWindow.NavigateToLoading();
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
