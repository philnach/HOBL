//--------------------------------------------------------------
//
// HOBL
// Copyright(c) Microsoft Corporation
// All rights reserved.
//
// MIT License
//
// Permission is hereby granted, free of charge, to any person obtaining
// a copy of this software and associated documentation files(the ""Software""),
// to deal in the Software without restriction, including without limitation the rights
// to use, copy, modify, merge, publish, distribute, sublicense, and / or sell copies
// of the Software, and to permit persons to whom the Software is furnished to do so,
// subject to the following conditions :
//
// The above copyright notice and this permission notice shall be included
// in all copies or substantial portions of the Software.
//
// THE SOFTWARE IS PROVIDED *AS IS*, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED,
// INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS
// FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.IN NO EVENT SHALL THE AUTHORS
// OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
// WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF
// OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
//
//--------------------------------------------------------------
using System;
using System.Net;
using System.Net.Sockets;
using System.Runtime.InteropServices;

#if WINDOWS
using System.Windows.Forms;
using SharpDX;
using SharpDX.Direct3D;
using SharpDX.Direct3D11;
using SharpDX.DXGI;
#else
using ObjCRuntime;
#endif

namespace ScreenServer
{
    class Program
    {
#if WINDOWS
        [DllImport("shcore.dll")]
        static extern uint SetProcessDpiAwareness(int value);

        [DllImport("user32.dll")]
        static extern bool EnumDisplaySettings(string? deviceName, int modeNum, ref DEVMODE devMode);

        [StructLayout(LayoutKind.Sequential)]
        struct DEVMODE
        {
            [MarshalAs(UnmanagedType.ByValTStr, SizeConst = 0x20)]
            public string dmDeviceName;
            public short dmSpecVersion;
            public short dmDriverVersion;
            public short dmSize;
            public short dmDriverExtra;
            public int dmFields;
            public int dmPositionX;
            public int dmPositionY;
            public int dmDisplayOrientation;
            public int dmDisplayFixedOutput;
            public short dmColor;
            public short dmDuplex;
            public short dmYResolution;
            public short dmTTOption;
            public short dmCollate;
            [MarshalAs(UnmanagedType.ByValTStr, SizeConst = 0x20)]
            public string dmFormName;
            public short dmLogPixels;
            public int dmBitsPerPel;
            public int dmPelsWidth;
            public int dmPelsHeight;
            public int dmDisplayFlags;
            public int dmDisplayFrequency;
            public int dmICMMethod;
            public int dmICMIntent;
            public int dmMediaType;
            public int dmDitherType;
            public int dmReserved1;
            public int dmReserved2;
            public int dmPanningWidth;
            public int dmPanningHeight;
        }
#else
        private const string CoreGraphics   = "/System/Library/Frameworks/CoreGraphics.framework/CoreGraphics";
        private const string CoreFoundation = "/System/Library/Frameworks/CoreFoundation.framework/CoreFoundation";

        [DllImport(CoreGraphics)]
        static extern uint CGMainDisplayID();

        [DllImport(CoreGraphics)]
        static extern int CGDisplayPixelsWide(uint display);

        [DllImport(CoreGraphics)]
        static extern int CGDisplayPixelsHigh(uint display);

        [DllImport(CoreGraphics)]
        static extern IntPtr CGDisplayCreateImage(uint displayID);

        [DllImport(CoreGraphics)]
        static extern IntPtr CGImageGetDataProvider(IntPtr imageRef);

        [DllImport(CoreGraphics)]
        static extern IntPtr CGDataProviderCopyData(IntPtr providerRef);

        [DllImport(CoreFoundation)]
        static extern IntPtr CFDataGetBytePtr(IntPtr theData);

        [DllImport(CoreFoundation)]
        static extern void CFRelease(IntPtr cf);
#endif
        static void Main(string[] args)
        {
            var listener = new TcpListener(IPAddress.Any, 8020);
            listener.Start();

            Console.WriteLine("Server started. Waiting for a client connection");

            using (var client = listener.AcceptTcpClient())
            {
                Console.WriteLine("Client connected");

                var monitorIndex = 0;

                if (args.Length > 0 && Int32.TryParse(args[0], out monitorIndex)) {
                    HandleConnection(client, monitorIndex);
                }
                else
                {
                    HandleConnection(client, 0);
                }
            }

            listener.Stop();
            Console.WriteLine("Client disconnected. Server terminating");
        }
#if WINDOWS
        static void HandleConnection(TcpClient client, int monitorIndex)
        {
            SetProcessDpiAwareness(2);

            using (var stream = client.GetStream())
            {
                var device = new SharpDX.Direct3D11.Device(DriverType.Hardware, DeviceCreationFlags.None);

                var factory = new Factory1();
                var adapter = factory.GetAdapter1(0);

                var output  = GetOutput(adapter, monitorIndex);
                var output1 = output.QueryInterface<Output1>();

                var duplication = output1.DuplicateOutput(device);

                var encoder = new QOIEncoder();

                SendResolution(output.Description, stream);

                while (client.Connected)
                {
                    try
                    {
                        HandleNextFrame(device, duplication, stream, encoder);
                    }
                    catch (SharpDXException ex)
                    {
                        // DXGI_ERROR_WAIT_TIMEOUT is expected if no new frame is available; continue waiting
                        if (ex.ResultCode.Code == SharpDX.DXGI.ResultCode.WaitTimeout.Code)
                        {
                            continue;
                        }
                        else
                        {
                            Console.WriteLine($"Error DX: {ex.Message}");
                            break;
                        }
                    }
                    catch (IOException)
                    {
                        break;
                    }
                    catch (Exception ex)
                    {
                        Console.WriteLine($"Error: {ex.Message}");
                        break;
                    }
                }

                duplication.Dispose();
                output1.Dispose();
                output.Dispose();
                adapter.Dispose();
                factory.Dispose();
                device.Dispose();
            }
        }

        static void HandleNextFrame(SharpDX.Direct3D11.Device device, OutputDuplication duplication,
                                    NetworkStream stream, QOIEncoder encoder)
        {
            OutputDuplicateFrameInformation frameInfo;
            SharpDX.DXGI.Resource desktopResource;

            duplication.TryAcquireNextFrame(-1, out frameInfo, out desktopResource);

            using (Texture2D texture = desktopResource.QueryInterface<Texture2D>())
            {
                var desc = texture.Description;

                desc.Format         = SharpDX.DXGI.Format.B8G8R8A8_UNorm;
                desc.Usage          = ResourceUsage.Staging;
                desc.CpuAccessFlags = CpuAccessFlags.Read;
                desc.BindFlags      = BindFlags.None;
                desc.OptionFlags    = ResourceOptionFlags.None;

                using (var stagingTexture = new Texture2D(device, desc))
                {
                    device.ImmediateContext.CopyResource(texture, stagingTexture);

                    var mapSource = device.ImmediateContext.MapSubresource(stagingTexture, 0, MapMode.Read, SharpDX.Direct3D11.MapFlags.None);

                    // Calculate the number of dirty rectangles
                    var rectSize   = Marshal.SizeOf(typeof(SharpDX.Mathematics.Interop.RawRectangle));
                    var bufferSize = frameInfo.TotalMetadataBufferSize;
                    var dirtyRects = new SharpDX.Mathematics.Interop.RawRectangle[bufferSize / rectSize];

                    var dirtyRectsCount = 0;

                    if (bufferSize > 0)
                    {
                        duplication.GetFrameDirtyRects(bufferSize, dirtyRects, out bufferSize);
                        dirtyRectsCount = bufferSize / rectSize;

                        // Send the number of dirty rectangles
                        var rectCountBytes = BitConverter.GetBytes(dirtyRectsCount);
                        stream.Write(rectCountBytes, 0, rectCountBytes.Length);
                    }

                    for (var rI = 0; rI < dirtyRectsCount; rI++)
                    {
                        var rect = dirtyRects[rI];

                        // Send rectangle dimensions
                        stream.Write(BitConverter.GetBytes(rect.Left),   0, 4);
                        stream.Write(BitConverter.GetBytes(rect.Top),    0, 4);
                        stream.Write(BitConverter.GetBytes(rect.Right),  0, 4);
                        stream.Write(BitConverter.GetBytes(rect.Bottom), 0, 4);

                        var regionWidth  = rect.Right - rect.Left;
                        var regionHeight = rect.Bottom - rect.Top;

                        var regionPixels = new int[regionWidth * regionHeight];

                        for (var row = rect.Top; row < rect.Bottom; row++)
                        {
                            // Compute the pointer for the start of this row's region.
                            // Each pixel is 4 bytes, so multiply the left offset by 4
                            var rowPtr = IntPtr.Add(
                                mapSource.DataPointer,
                                row * mapSource.RowPitch + rect.Left * 4
                            );

                            var destIndex = (row - rect.Top) * regionWidth;

                            Marshal.Copy(rowPtr, regionPixels, destIndex, regionWidth);
                        }

                        for (var i = 0; i < regionPixels.Length; i++)
                        {
                            // Convert BGRA to RGBA
                            var p = (uint)regionPixels[i];
                            regionPixels[i] = (int)((p & 0xFF00FF00)
                                                | ((p & 0x00FF0000) >> 16)
                                                | ((p & 0x000000FF) << 16));
                        }

                        if (!encoder.Encode(regionWidth, regionHeight, regionPixels, true, false))
                        {
                            Console.WriteLine("Encoding failed for region");
                            break;
                        }

                        var regionEncodedSize = encoder.GetEncodedSize();

                        // Send region-encoded data size
                        var regionSizeBytes = BitConverter.GetBytes(regionEncodedSize);
                        stream.Write(regionSizeBytes, 0, regionSizeBytes.Length);

                        // Send the QOI‑encoded region data
                        var regionQoiData = encoder.GetEncoded();
                        stream.Write(regionQoiData, 0, regionEncodedSize);
                    }

                    stream.Flush();
                    device.ImmediateContext.UnmapSubresource(stagingTexture, 0);
                }
            }

            duplication.ReleaseFrame();
            desktopResource.Dispose();
        }

        static Output GetOutput(Adapter adapter, int monitorIndex)
        {
            var deviceName = Screen.AllScreens[monitorIndex].DeviceName;

            for (var i = 0; i < Screen.AllScreens.Length; i++)
            {
                var output = adapter.GetOutput(i);

                if (string.Equals(output.Description.DeviceName, deviceName, StringComparison.OrdinalIgnoreCase))
                {
                    return output;
                }

                output.Dispose();
            }

            throw new InvalidOperationException($"Could not find a DXGI output for \"{deviceName}\"");
        }

        static void SendResolution(OutputDescription outputDesc, NetworkStream stream)
        {
            var width  = outputDesc.DesktopBounds.Right  - outputDesc.DesktopBounds.Left;
            var height = outputDesc.DesktopBounds.Bottom - outputDesc.DesktopBounds.Top;

            byte[] resolutionData = new byte[8];

            System.Buffer.BlockCopy(BitConverter.GetBytes(height), 0, resolutionData, 0, 4);
            System.Buffer.BlockCopy(BitConverter.GetBytes(width),  0, resolutionData, 4, 4);

            stream.Write(resolutionData, 0, resolutionData.Length);
            stream.Flush();
        }
#else
        static void HandleConnection(TcpClient client, int monitorIndex)
        {
            using (var stream = client.GetStream())
            {
                var encoder = new QOIEncoder();

                SendResolution(stream);

                while (client.Connected)
                {
                    try
                    {
                        HandleNextFrame(stream, encoder);
                    }
                    catch (IOException)
                    {
                        break;
                    }
                    catch (Exception ex)
                    {
                        Console.WriteLine($"Error: {ex.Message}");
                        break;
                    }
                }
            }
        }

        static void HandleNextFrame(NetworkStream stream, QOIEncoder encoder)
        {
            var displayId    = CGMainDisplayID();
            var origImageRef = CGDisplayCreateImage(displayId);

            var origImage = Runtime.GetINativeObject<CGImage>(origImageRef, false);
            CFRelease(origImageRef);

            using var image = ScaleImageByHalf(origImage);

            if (image is null) return;

            var w = (int)image.Width;
            var h = (int)image.Height;

            var provider = CGImageGetDataProvider(image.Handle);
            var dataRef  = CGDataProviderCopyData(provider);

            var rawData = new int[w * h];
            var srcPtr  = CFDataGetBytePtr(dataRef);

            for (int y = 0; y < h; y++)
            {
                var rowStart = srcPtr + y * image.BytesPerRow;
                Marshal.Copy(rowStart, rawData, y * w, w);
            }

            // Always send the full screen as a single "dirty" rect
            var rectCountBytes = BitConverter.GetBytes(1);
            stream.Write(rectCountBytes, 0, rectCountBytes.Length);

            // Send rectangle dimensions
            stream.Write(BitConverter.GetBytes(0), 0, 4);
            stream.Write(BitConverter.GetBytes(0), 0, 4);
            stream.Write(BitConverter.GetBytes(w), 0, 4);
            stream.Write(BitConverter.GetBytes(h), 0, 4);

            if (!encoder.Encode(w, h, rawData, true, false))
            {
                Console.WriteLine("Encoding failed for region");
                return;
            }

            var encodedSize = encoder.GetEncodedSize();

            // Send region-encoded data size
            var sizeBytes = BitConverter.GetBytes(encodedSize);
            stream.Write(sizeBytes, 0, sizeBytes.Length);

            var qoiData = encoder.GetEncoded();
            stream.Write(qoiData, 0, encodedSize);

            stream.Flush();

            CFRelease(dataRef);
        }

        static void SendResolution(NetworkStream stream)
        {
            var displayId = CGMainDisplayID();

            var width  = CGDisplayPixelsWide(displayId);
            var height = CGDisplayPixelsHigh(displayId);

            var resolutionData = new byte[8];

            Buffer.BlockCopy(BitConverter.GetBytes(height), 0, resolutionData, 0, 4);
            Buffer.BlockCopy(BitConverter.GetBytes(width),  0, resolutionData, 4, 4);

            stream.Write(resolutionData, 0, resolutionData.Length);
            stream.Flush();
        }

        static CGImage? ScaleImageByHalf(CGImage? sourceImage)
        {   
            if (sourceImage is null) return null;

            var scaledWidth  = sourceImage.Width / 2;
            var scaledHeight = sourceImage.Height / 2;

            using var colorSpace = CGColorSpace.CreateDeviceRGB();

            using var context = new CGBitmapContext(
                IntPtr.Zero,
                scaledWidth,
                scaledHeight,
                sourceImage.BitsPerComponent,
                0,
                colorSpace,
                CGBitmapFlags.ByteOrder32Big | (CGBitmapFlags)CGImageAlphaInfo.PremultipliedLast
            );

            context.InterpolationQuality = CGInterpolationQuality.High;
            context.DrawImage(new CGRect(0, 0, scaledWidth, scaledHeight), sourceImage);

            return context.ToImage();
        }
#endif
    }
}
