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
using SACA.WindowsApp.Services;

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

            SeverityTextBlock.Text = $"{AppLanguage.T("severity_level")}: {response.TriageLevel}";
            RecommendationTextBlock.Text = $"{AppLanguage.T("recommendation")}: {response.Recommendation}";
            SummaryTextBlock.Text = string.Join(", ", response.Summary);
        }

        private void StartAgain_Click(object sender, RoutedEventArgs e)
        {
            _mainWindow.CurrentRequest = new TriageRequest();
            AppLanguage.SetLanguage("English");
            _mainWindow.NavigateToSplash();
        }

        private void Ok_Click(object sender, RoutedEventArgs e)
        {
            Application.Current.Shutdown();
        }
    }
}
