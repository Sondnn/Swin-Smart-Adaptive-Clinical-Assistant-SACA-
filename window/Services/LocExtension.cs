using System;
using System.Windows.Markup;

namespace SACA.WindowsApp.Services
{
    public class LocExtension : MarkupExtension
    {
        public LocExtension()
        {
            Key = "";
        }

        public LocExtension(string key)
        {
            Key = key;
        }

        public string Key { get; set; }

        public override object ProvideValue(IServiceProvider serviceProvider)
        {
            return AppLanguage.T(Key);
        }
    }
}
