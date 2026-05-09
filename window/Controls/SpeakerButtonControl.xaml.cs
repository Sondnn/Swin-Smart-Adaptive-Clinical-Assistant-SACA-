using System.Windows;
using System.Windows.Controls;
using SACA.WindowsApp.Services;

namespace SACA.WindowsApp.Controls
{
    public partial class SpeakerButtonControl : UserControl
    {
        public static readonly DependencyProperty TextKeyProperty = DependencyProperty.Register(
            nameof(TextKey),
            typeof(string),
            typeof(SpeakerButtonControl),
            new PropertyMetadata(""));

        public string TextKey
        {
            get => (string)GetValue(TextKeyProperty);
            set => SetValue(TextKeyProperty, value);
        }

        public SpeakerButtonControl()
        {
            InitializeComponent();
        }

        private void SpeakButton_Click(object sender, RoutedEventArgs e)
        {
            TextToSpeechService.Speak(AppLanguage.T(TextKey));
        }
    }
}
