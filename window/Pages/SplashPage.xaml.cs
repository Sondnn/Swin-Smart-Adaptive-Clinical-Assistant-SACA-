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
    /// Interaction logic for SplashPage.xaml
    /// </summary>
    public partial class SplashPage : UserControl
    {

        private readonly MainWindow _mainWindow;

        public SplashPage(MainWindow mainWindow)
        {
            InitializeComponent();
            _mainWindow = mainWindow;
        }

        private void English_Click(object sender, System.Windows.RoutedEventArgs e)
        {
            AppLanguage.SetLanguage("English");
            _mainWindow.CurrentRequest.Language = "English";
            _mainWindow.NavigateToStart();
        }

        private void Walmajarri_Click(object sender, System.Windows.RoutedEventArgs e)
        {
            AppLanguage.SetLanguage("Walmajarri");
            _mainWindow.CurrentRequest.Language = "Walmajarri";
            _mainWindow.NavigateToStart();
        }

    }
}
