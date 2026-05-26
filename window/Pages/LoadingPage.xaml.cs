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
    /// Interaction logic for LoadingPage.xaml
    public partial class LoadingPage : UserControl
    {
        private readonly MainWindow _mainWindow;
        private readonly TriageApiService _apiService = new();

        public LoadingPage(MainWindow mainWindow)
        {
            InitializeComponent();
            _mainWindow = mainWindow;
            Loaded += LoadingPage_Loaded;
        }

        private async void LoadingPage_Loaded(object sender, RoutedEventArgs e)
        {
            try
            {
                var result = await _apiService.AnalyseAsync(_mainWindow.CurrentRequest);
                _mainWindow.NavigateToResult(result);
            }
            catch (Exception ex)
            {
                MessageBox.Show(ex.Message, AppLanguage.T("assessment"));
                _mainWindow.NavigateToSymptoms();
            }
        }
    }
}
