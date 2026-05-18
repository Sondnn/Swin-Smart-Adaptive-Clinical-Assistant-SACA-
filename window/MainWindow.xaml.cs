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
        private TriageResponse? _lastResponse;

        public MainWindow()
        {
            InitializeComponent();
            NavigateToSplash();
        }

        public void NavigateToSplash()
        {
            MainContent.Content = new SplashPage(this);
            UpdateLanguageSwitcherVisibility();
        }

        public void NavigateToStart()
        {
            MainContent.Content = new StartPage(this);
            UpdateLanguageSwitcherVisibility();
        }

        public void NavigateToPatientInfo()
        {
            MainContent.Content = new PatientInfoPage(this);
            UpdateLanguageSwitcherVisibility();
        }

        public void NavigateToAge()
        {
            MainContent.Content = new AgePage(this);
            UpdateLanguageSwitcherVisibility();
        }

        public void NavigateToSymptoms()
        {
            MainContent.Content = new SymptomsPage(this);
            UpdateLanguageSwitcherVisibility();
        }

        public void NavigateToSeverity()
        {
            MainContent.Content = new SeverityPage(this);
            UpdateLanguageSwitcherVisibility();
        }

        public void NavigateToDuration()
        {
            MainContent.Content = new DurationPage(this);
            UpdateLanguageSwitcherVisibility();
        }

        public void NavigateToSymptomsHistory()
        {
            MainContent.Content = new SymptomsHistoryPage(this);
            UpdateLanguageSwitcherVisibility();
        }

        public void NavigateToChronicConditions()
        {
            MainContent.Content = new ChronicConditionsPage(this);
            UpdateLanguageSwitcherVisibility();
        }

        public void NavigateToSickContact()
        {
            MainContent.Content = new SickContactPage(this);
            UpdateLanguageSwitcherVisibility();
        }

        public void NavigateToLoading()
        {
            MainContent.Content = new LoadingPage(this);
            UpdateLanguageSwitcherVisibility();
        }

        public void NavigateToResult(TriageResponse response)
        {
            _lastResponse = response;
            MainContent.Content = new ResultPage(this, response);
            UpdateLanguageSwitcherVisibility();
        }

        private void EnglishLanguage_Click(object sender, RoutedEventArgs e)
        {
            ChangeLanguage("English");
        }

        private void WalmajarriLanguage_Click(object sender, RoutedEventArgs e)
        {
            ChangeLanguage("Walmajarri");
        }

        private void ChangeLanguage(string language)
        {
            AppLanguage.SetLanguage(language);
            CurrentRequest.Language = language;
            RefreshCurrentPage();
        }

        private void RefreshCurrentPage()
        {
            switch (MainContent.Content)
            {
                case SplashPage:
                    NavigateToSplash();
                    break;
                case StartPage:
                    NavigateToStart();
                    break;
                case PatientInfoPage:
                    NavigateToPatientInfo();
                    break;
                case AgePage:
                    NavigateToAge();
                    break;
                case SymptomsPage:
                    NavigateToSymptoms();
                    break;
                case SeverityPage:
                    NavigateToSeverity();
                    break;
                case DurationPage:
                    NavigateToDuration();
                    break;
                case SymptomsHistoryPage:
                    NavigateToSymptomsHistory();
                    break;
                case ChronicConditionsPage:
                    NavigateToChronicConditions();
                    break;
                case SickContactPage:
                    NavigateToSickContact();
                    break;
                case ResultPage when _lastResponse != null:
                    NavigateToResult(_lastResponse);
                    break;
            }
        }

        private void UpdateLanguageSwitcherVisibility()
        {
            LanguageSwitcher.Visibility = MainContent.Content is SplashPage or LoadingPage
                ? Visibility.Collapsed
                : Visibility.Visible;

            bool isEnglish = CurrentRequest.Language.Equals("English", System.StringComparison.OrdinalIgnoreCase);
            EnglishButton.Background = isEnglish ? FindBrush("AccentBrush") : FindBrush("InputBackgroundBrush");
            EnglishButton.Foreground = isEnglish ? Brushes.White : FindBrush("PrimaryTextBrush");
            EnglishButton.BorderBrush = isEnglish ? FindBrush("AccentBrush") : FindBrush("BorderBrush");

            WalmajarriButton.Background = isEnglish ? FindBrush("InputBackgroundBrush") : FindBrush("AccentBrush");
            WalmajarriButton.Foreground = isEnglish ? FindBrush("PrimaryTextBrush") : Brushes.White;
            WalmajarriButton.BorderBrush = isEnglish ? FindBrush("BorderBrush") : FindBrush("AccentBrush");
        }

        private Brush FindBrush(string key)
        {
            return TryFindResource(key) as Brush ?? Brushes.Transparent;
        }
    }
}
