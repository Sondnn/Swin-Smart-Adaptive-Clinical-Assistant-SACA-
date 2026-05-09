using System;
using System.Runtime.InteropServices;
using System.Threading.Tasks;

namespace SACA.WindowsApp.Services
{
    public static class TextToSpeechService
    {
        private static object? _voice;

        public static void Speak(string text)
        {
            if (string.IsNullOrWhiteSpace(text))
            {
                return;
            }

            Task.Run(() =>
            {
                try
                {
                    object voice = GetVoice();

                    // SAPI flag 2 stops any current speech before starting the new instruction.
                    voice.GetType().InvokeMember("Speak", System.Reflection.BindingFlags.InvokeMethod, null, voice, new object[] { "", 2 });
                    voice.GetType().InvokeMember("Speak", System.Reflection.BindingFlags.InvokeMethod, null, voice, new object[] { text, 1 });
                }
                catch (COMException)
                {
                    // Text-to-speech is an accessibility enhancement; do not interrupt the form if SAPI is unavailable.
                }
            });
        }

        private static object GetVoice()
        {
            if (_voice != null)
            {
                return _voice;
            }

            Type voiceType = Type.GetTypeFromProgID("SAPI.SpVoice")
                ?? throw new InvalidOperationException("Windows text-to-speech is not available.");

            _voice = Activator.CreateInstance(voiceType)
                ?? throw new InvalidOperationException("Windows text-to-speech could not be started.");

            return _voice;
        }
    }
}
