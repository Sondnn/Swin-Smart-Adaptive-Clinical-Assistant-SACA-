using System.Text;
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
using SACA.WindowsApp.Pages;

namespace SACA.WindowsApp
{
    public partial class MainWindow : Window
    {
        public TriageRequest CurrentRequest { get; set; } = new();

        public MainWindow()
        {
            InitializeComponent();
            NavigateToSplash();
        }

        public void NavigateToSplash()
        {
            MainContent.Content = new SplashPage(this);
        }

        public void NavigateToStart()
        {
            MainContent.Content = new StartPage(this);
        }

        public void NavigateToPatientInfo()
        {
            MainContent.Content = new PatientInfoPage(this);
        }

        public void NavigateToSymptoms()
        {
            MainContent.Content = new SymptomsPage(this);
        }

        public void NavigateToDuration()
        {
            MainContent.Content = new DurationPage(this);
        }

        public void NavigateToLoading()
        {
            MainContent.Content = new LoadingPage(this);
        }

        public void NavigateToResult(TriageResponse response)
        {
            MainContent.Content = new ResultPage(this, response);
        }
    }
}