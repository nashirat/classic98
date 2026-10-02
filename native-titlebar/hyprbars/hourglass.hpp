#pragma once

#include <gif_lib.h>
#include <dlfcn.h>
#include <algorithm>
#include <array>
#include <filesystem>
#include <string>
#include <vector>

namespace Classic98 {
struct Title {
    std::string text;
    bool busy = false;
};

inline Title agentTitle(const std::string& app, const std::string& title) {
    // Omarchy signals an active agent with a leading Braille spinner.
    const bool agent = app == "org.omarchy.agent" || (app == "foot" && title.find(" | ") != std::string::npos);
    if (agent && title.size() > 3 &&
        static_cast<unsigned char>(title[0]) == 0xe2 &&
        static_cast<unsigned char>(title[1]) >= 0xa0 && static_cast<unsigned char>(title[1]) <= 0xa3 &&
        static_cast<unsigned char>(title[2]) >= 0x80 && static_cast<unsigned char>(title[2]) <= 0xbf && title[3] == ' ')
        return {title.substr(4), true};
    return {title, false};
}

struct Frame {
    std::vector<unsigned char> rgba;
    int delayMs = 100;
};
struct Animation {
    int width = 0, height = 0, durationMs = 0;
    std::vector<Frame> frames;
    size_t frameAt(int elapsedMs) const {
        if (frames.empty() || durationMs <= 0) return 0;
        int t = elapsedMs % durationMs;
        for (size_t i = 0; i < frames.size(); ++i) {
            if (t < frames[i].delayMs) return i;
            t -= frames[i].delayMs;
        }
        return 0;
    }
};

inline Animation loadHourglass(const std::filesystem::path& path) {
    int error = 0;
    GifFileType* gif = DGifOpenFileName(path.c_str(), &error);
    if (!gif) return {};
    struct Close { GifFileType* gif; ~Close() { int e; DGifCloseFile(gif, &e); } } close{gif};
    if (gif->SWidth < 1 || gif->SHeight < 1 || gif->SWidth > 512 || gif->SHeight > 512 || DGifSlurp(gif) != GIF_OK ||
        gif->ImageCount < 1 || gif->ImageCount > 500) return {};
    const int w = gif->SWidth, h = gif->SHeight;
    std::array<unsigned char, 4> background{255, 255, 255, 255};
    if (gif->SColorMap && gif->SBackGroundColor < gif->SColorMap->ColorCount) {
        const auto c = gif->SColorMap->Colors[gif->SBackGroundColor];
        background = {c.Red, c.Green, c.Blue, 255};
    }
    std::vector<unsigned char> canvas(w * h * 4);
    for (int i = 0; i < w * h; ++i) std::copy(background.begin(), background.end(), canvas.begin() + i * 4);
    Animation result;
    int minX = w, minY = h, maxX = -1, maxY = -1;
    for (int index = 0; index < gif->ImageCount; ++index) {
        const auto& image = gif->SavedImages[index];
        const auto& d = image.ImageDesc;
        if (d.Left < 0 || d.Top < 0 || d.Width < 1 || d.Height < 1 || d.Left + d.Width > w || d.Top + d.Height > h) return {};
        const auto* palette = d.ColorMap ? d.ColorMap : gif->SColorMap;
        if (!palette) return {};
        GraphicsControlBlock control{};
        control.TransparentColor = NO_TRANSPARENT_COLOR;
        DGifSavedExtensionToGCB(gif, index, &control);
        const auto previous = canvas;
        for (int y = 0; y < d.Height; ++y) for (int x = 0; x < d.Width; ++x) {
            const int color = image.RasterBits[y * d.Width + x];
            if (color == control.TransparentColor) continue;
            if (color >= palette->ColorCount) return {};
            const auto c = palette->Colors[color];
            const int p = ((y + d.Top) * w + x + d.Left) * 4;
            canvas[p] = c.Red; canvas[p + 1] = c.Green; canvas[p + 2] = c.Blue; canvas[p + 3] = 255;
        }
        Frame frame{canvas, std::max(20, control.DelayTime * 10)};
        // Make only edge-connected near-white background transparent at render
        // time. Enclosed white glass/sand stays white. The GIF is unchanged.
        std::vector<int> queue;
        std::vector<bool> seen(w * h, false);
        const auto enqueue = [&](int x, int y) {
            if (x < 0 || y < 0 || x >= w || y >= h) return;
            int p = y * w + x;
            if (seen[p]) return;
            seen[p] = true;
            if (frame.rgba[p * 4] >= 245 && frame.rgba[p * 4 + 1] >= 245 && frame.rgba[p * 4 + 2] >= 245) queue.push_back(p);
        };
        for (int x = 0; x < w; ++x) { enqueue(x, 0); enqueue(x, h - 1); }
        for (int y = 0; y < h; ++y) { enqueue(0, y); enqueue(w - 1, y); }
        for (size_t i = 0; i < queue.size(); ++i) {
            int p = queue[i], x = p % w, y = p / w;
            frame.rgba[p * 4] = frame.rgba[p * 4 + 1] = frame.rgba[p * 4 + 2] = frame.rgba[p * 4 + 3] = 0;
            enqueue(x - 1, y); enqueue(x + 1, y); enqueue(x, y - 1); enqueue(x, y + 1);
        }
        for (int y = 0; y < h; ++y) for (int x = 0; x < w; ++x) {
            if (!frame.rgba[(y * w + x) * 4 + 3]) continue;
            minX = std::min(minX, x); maxX = std::max(maxX, x);
            minY = std::min(minY, y); maxY = std::max(maxY, y);
        }
        result.durationMs += frame.delayMs;
        result.frames.push_back(std::move(frame));
        if (control.DisposalMode == DISPOSE_BACKGROUND) {
            for (int y = d.Top; y < d.Top + d.Height; ++y) for (int x = d.Left; x < d.Left + d.Width; ++x)
                std::copy(background.begin(), background.end(), canvas.begin() + (y * w + x) * 4);
        } else if (control.DisposalMode == DISPOSE_PREVIOUS) canvas = previous;
    }
    if (maxX < minX || maxY < minY) return {};
    result.width = maxX - minX + 1; result.height = maxY - minY + 1;
    for (auto& frame : result.frames) {
        std::vector<unsigned char> cropped(result.width * result.height * 4);
        for (int y = 0; y < result.height; ++y)
            std::copy_n(frame.rgba.begin() + ((y + minY) * w + minX) * 4, result.width * 4, cropped.begin() + y * result.width * 4);
        frame.rgba = std::move(cropped);
    }
    return result;
}

inline const Animation& hourglass() {
    static const Animation animation = [] {
        Dl_info info{};
        if (!dladdr(reinterpret_cast<void*>(&hourglass), &info) || !info.dli_fname) return Animation{};
        return loadHourglass(std::filesystem::path(info.dli_fname).parent_path() / "../assets/hourglass-original.gif");
    }();
    return animation;
}
}
