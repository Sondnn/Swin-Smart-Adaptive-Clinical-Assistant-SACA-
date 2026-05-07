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
using SACA.WindowsApp.Models;

namespace SACA.WindowsApp.Pages
{
    /// <summary>
    /// Interaction logic for ResultPage.xaml
    /// </summary>

    public partial class ResultPage : UserControl
    {
        private readonly MainWindow _mainWindow;

        public ResultPage(MainWindow mainWindow, TriageResponse response)
        {
            InitializeComponent();
            _mainWindow = mainWindow;

            SeverityTextBlock.Text = $"Severity Level: {response.TriageLevel}";
            RecommendationTextBlock.Text = $"Recommendation: {response.Recommendation}";
            SummaryTextBlock.Text = string.Join(", ", response.Summary);
        }

        private void StartAgain_Click(object sender, RoutedEventArgs e)
        {
            _mainWindow.CurrentRequest = new TriageRequest();
            _mainWindow.NavigateToSplash();
        }

        private void Ok_Click(object sender, RoutedEventArgs e)
        {
            Application.Current.Shutdown();
        }
    }
}
