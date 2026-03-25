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

#define INITGUID
#include <windows.h>
#include <dxcore.h>
#include <wrl.h>
#include <iostream>
#include <vector>
#include <set>
#include <string>
#include <iomanip>

using Microsoft::WRL::ComPtr;

static bool GetAdapterName(ComPtr<IDXCoreAdapter> adapter, std::string &outDesc)
{
    outDesc.clear();

    if (!adapter->IsPropertySupported(DXCoreAdapterProperty::DriverDescription))
        return false;

    size_t descSize = 0;
    if (FAILED(adapter->GetPropertySize(DXCoreAdapterProperty::DriverDescription, &descSize)) || descSize == 0)
        return false;

    std::vector<char> buffer(descSize);
    if (SUCCEEDED(adapter->GetProperty(DXCoreAdapterProperty::DriverDescription, descSize, buffer.data())))
    {
        outDesc.assign(buffer.data());
        return true;
    }

    return false;
}

static bool TryGetInstanceLuid(ComPtr<IDXCoreAdapter> adapter,
                               uint32_t &high, uint32_t &low)
{
    high = low = 0;

    if (!adapter->IsPropertySupported(DXCoreAdapterProperty::InstanceLuid))
        return false;

    LUID luid = {};
    if (FAILED(adapter->GetProperty(DXCoreAdapterProperty::InstanceLuid,
                                    sizeof(luid), &luid)))
        return false;

    high = static_cast<uint32_t>(luid.HighPart);
    low  = static_cast<uint32_t>(luid.LowPart);
    return true;
}

static bool GetAdapterSimpleType(ComPtr<IDXCoreAdapter> adapter, std::string &outType)
{
    outType.clear();

    if (!adapter)
        return false;

    if (adapter->IsPropertySupported(DXCoreAdapterProperty::IsHardware))
    {
        bool isHardware = true;
        size_t sz = 0;
        if (SUCCEEDED(adapter->GetPropertySize(DXCoreAdapterProperty::IsHardware, &sz)) &&
            sz == sizeof(bool) &&
            SUCCEEDED(adapter->GetProperty(DXCoreAdapterProperty::IsHardware, sz, &isHardware)))
        {
            if (!isHardware)
            {
                outType = "Software Adapter";
                return true;
            }
        }
    }

    if (adapter->IsAttributeSupported(DXCORE_HARDWARE_TYPE_ATTRIBUTE_NPU))
    {
        outType = "NPU";
        return true;
    }

    if (adapter->IsAttributeSupported(DXCORE_HARDWARE_TYPE_ATTRIBUTE_MEDIA_ACCELERATOR))
    {
        outType = "Media Accelerator";
        return true;
    }

    if (adapter->IsAttributeSupported(DXCORE_HARDWARE_TYPE_ATTRIBUTE_COMPUTE_ACCELERATOR))
    {
        outType = "Compute Accelerator";
        return true;
    }

    if (adapter->IsAttributeSupported(DXCORE_HARDWARE_TYPE_ATTRIBUTE_GPU))
    {
        if (adapter->IsPropertySupported(DXCoreAdapterProperty::IsIntegrated))
        {
            bool isIntegrated = false;
            size_t sz = 0;
            if (SUCCEEDED(adapter->GetPropertySize(DXCoreAdapterProperty::IsIntegrated, &sz)) &&
                sz == sizeof(bool) &&
                SUCCEEDED(adapter->GetProperty(DXCoreAdapterProperty::IsIntegrated, sz, &isIntegrated)))
            {
                outType = (isIntegrated ? "Integrated GPU" : "Discrete GPU");
                return true;
            }
        }

        return false;
    }

    return false;
}

int main()
{
    HRESULT hr = S_OK;

    ComPtr<IDXCoreAdapterFactory> factory;
    hr = ::DXCoreCreateAdapterFactory(IID_PPV_ARGS(&factory));
    if (FAILED(hr))
    {
        return 0;
    }

    const GUID filters[] =
    {
        DXCORE_ADAPTER_ATTRIBUTE_D3D12_GRAPHICS,
        DXCORE_ADAPTER_ATTRIBUTE_D3D11_GRAPHICS,
        DXCORE_ADAPTER_ATTRIBUTE_D3D12_GENERIC_ML,
        DXCORE_ADAPTER_ATTRIBUTE_D3D12_GENERIC_MEDIA,
        DXCORE_ADAPTER_ATTRIBUTE_D3D12_GRAPHICS,
        DXCORE_ADAPTER_ATTRIBUTE_D3D12_CORE_COMPUTE,
        DXCORE_HARDWARE_TYPE_ATTRIBUTE_GPU,
        DXCORE_HARDWARE_TYPE_ATTRIBUTE_COMPUTE_ACCELERATOR,
        DXCORE_HARDWARE_TYPE_ATTRIBUTE_NPU,
        DXCORE_HARDWARE_TYPE_ATTRIBUTE_MEDIA_ACCELERATOR,
    };

    std::set<uint64_t> seenLUIDs;

    for (const GUID &g : filters)
    {
        ComPtr<IDXCoreAdapterList> list;
        hr = factory->CreateAdapterList(1, &g, IID_PPV_ARGS(&list));
        if (FAILED(hr) || !list)
            continue;

        uint32_t count = list->GetAdapterCount();

        for (uint32_t i = 0; i < count; i++)
        {
            ComPtr<IDXCoreAdapter> adapter;
            if (FAILED(list->GetAdapter(i, IID_PPV_ARGS(&adapter))) || !adapter)
                continue;

            uint32_t high = 0, low = 0;
            if (!TryGetInstanceLuid(adapter, high, low))
                continue;

            // Deduplicate
            uint64_t key = (uint64_t(high) << 32) | uint64_t(low);
            if (seenLUIDs.count(key))
                continue;
            seenLUIDs.insert(key);

            std::string name;
            bool nameOk = GetAdapterName(adapter, name);

            std::string type;
            bool typeOk = GetAdapterSimpleType(adapter, type);

            // Format: luid,adapter_name,adapter_type
            std::cout
                << "0x"
                << std::hex << std::uppercase << std::setw(8) << std::setfill('0') << high
                << "_0x" << std::setw(8) << std::setfill('0') << low
                << ",";

            if (nameOk)
                std::cout << std::quoted(name);

            std::cout << ",";

            if (typeOk)
                std::cout << std::quoted(type);

            std::cout << std::dec << std::setfill(' ') << std::nouppercase << "\n";
        }
    }

    return 0;
}
