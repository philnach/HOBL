#if WINDOWS
using System.Diagnostics.Tracing;

namespace InputInject
{
    [EventSource(Name = "InputInject.EventLogger", Guid ="150A3791-7792-452D-858C-15D647ECB48F")]
    public sealed class EtwLogger : EventSource
    {
        public static EtwLogger Etw = new EtwLogger();

        public class InputInjectTasks
        {
            public const EventTask Task = (EventTask)1;
        }

        private enum EtwEventId
        {
            Task = 1,
        }

        [Event((int)EtwEventId.Task, Opcode = EventOpcode.Info, Task = InputInjectTasks.Task)]
        public void Task(string tag) { WriteEvent((int)EtwEventId.Task, tag); }
    }
}
#endif
