#include "borderDeco.hpp"

#include <algorithm>
#include <array>
#include <string_view>

#include <hyprland/src/Compositor.hpp>
#include <hyprland/src/desktop/state/FocusState.hpp>
#include <hyprland/src/desktop/view/Window.hpp>
#include <hyprland/src/render/Renderer.hpp>
#include <hyprutils/memory/Casts.hpp>
using namespace Hyprutils::Memory;
using namespace Render::GL;
#include "BorderppPassElement.hpp"
#include "globals.hpp"

// Rings outer to inner as palette indices (D dark, L light, M mid). Top/left use
// TL, bottom/right use BR: raised outer bevel, flat face, sunken inner ridge.
static constexpr std::string_view FRAME_TL = "DLLMMMD";
static constexpr std::string_view FRAME_BR = "DDMMMLD";
static constexpr double           FRAME_SIZE = FRAME_TL.size();

CBordersPlusPlus::CBordersPlusPlus(PHLWINDOW pWindow) : IHyprWindowDecoration(pWindow), m_pWindow(pWindow) {
    m_lastWindowPos  = pWindow->position(Desktop::View::IGeometric::GEOMETRIC_CURRENT);
    m_lastWindowSize = pWindow->size(Desktop::View::IGeometric::GEOMETRIC_CURRENT);
}

CBordersPlusPlus::~CBordersPlusPlus() {
    damageEntire();
}

SDecorationPositioningInfo CBordersPlusPlus::getPositioningInfo() {
    SDecorationPositioningInfo info;
    info.policy   = DECORATION_POSITION_STICKY;
    info.reserved = true;
    info.priority = 9990;
    info.edges    = DECORATION_EDGE_BOTTOM | DECORATION_EDGE_LEFT | DECORATION_EDGE_RIGHT | DECORATION_EDGE_TOP;

    const double T = FRAME_SIZE;
    info.desiredExtents = {{T, T}, {T, T}};

    return info;
}

void CBordersPlusPlus::onPositioningReply(const SDecorationPositioningReply& reply) {
    m_bAssignedGeometry = reply.assignedGeometry;
}

uint64_t CBordersPlusPlus::getDecorationFlags() {
    return DECORATION_PART_OF_MAIN_WINDOW;
}

eDecorationLayer CBordersPlusPlus::getDecorationLayer() {
    return DECORATION_LAYER_OVER;
}

std::string CBordersPlusPlus::getDisplayName() {
    return "Borders++";
}

void CBordersPlusPlus::draw(PHLMONITOR pMonitor, const float& a) {
    if (!validMapped(m_pWindow))
        return;

    const auto PWINDOW = m_pWindow.lock();

    if (!PWINDOW->m_ruleApplicator->decorate().valueOrDefault())
        return;

    CBorderPPPassElement::SBorderPPData data;
    data.deco = this;

    g_pHyprRenderer->m_renderPass.add(makeUnique<CBorderPPPassElement>(data));
}

// Classic 98 frame, after an fvwm3 window border: {dark, light, mid}.
static constexpr std::array<uint32_t, 3> ACTIVE = {0x202020, 0x676767, 0x4d4d4d}, INACTIVE = {0x101010, 0x474747, 0x2d2d2d};
static constexpr int      NOTCH       = 27; // groove distance from each corner: frame + title bar height

static CHyprColor rgb(uint32_t c, float a) {
    return CHyprColor{((c >> 16) & 0xff) / 255.0, ((c >> 8) & 0xff) / 255.0, (c & 0xff) / 255.0, a};
}

void CBordersPlusPlus::drawPass(PHLMONITOR pMonitor, const float& a) {
    const auto PWINDOW = m_pWindow.lock();
    const int  T       = FRAME_TL.size();
    const auto& PAL    = PWINDOW == Desktop::focusState()->window() ? ACTIVE : INACTIVE;
    const auto  col    = [&](char c) { return PAL[c == 'D' ? 0 : c == 'L' ? 1 : 2]; };
    const auto  GROOVE_DARK = PAL[0], GROOVE_LIGHT = PAL[1];

    if (m_bAssignedGeometry.width < m_seExtents.topLeft.x + 1 || m_bAssignedGeometry.height < m_seExtents.topLeft.y + 1)
        return;

    const auto PWORKSPACE      = PWINDOW->m_workspace;
    const auto WORKSPACEOFFSET = PWORKSPACE && !PWINDOW->m_pinned ? PWORKSPACE->m_renderOffset->value() : Vector2D();

    CBox       box = m_bAssignedGeometry;
    box.translate(g_pDecorationPositioner->getEdgeDefinedPoint(DECORATION_EDGE_BOTTOM | DECORATION_EDGE_LEFT | DECORATION_EDGE_RIGHT | DECORATION_EDGE_TOP, PWINDOW));
    box.translate(PWINDOW->m_floatingOffset - pMonitor->m_position + WORKSPACEOFFSET);

    if (box.width < T * 2 + 1 || box.height < T * 2 + 1)
        return;

    g_pHyprOpenGL->scissor(nullptr);

    const auto S    = pMonitor->m_scale;
    auto       fill = [&](double x, double y, double w, double h, uint32_t c) {
        CBox b{box.x + x, box.y + y, w, h};
        g_pHyprOpenGL->renderRect(b.scale(S).round(), rgb(c, a), {.round = 0});
    };

    const double W = box.width, H = box.height;
    for (int i = 0; i < T; ++i) {
        const double w = W - i * 2, h = H - i * 2;
        fill(i, i, w - 1, 1, col(FRAME_TL[i]));         // top
        fill(i, i + 1, 1, h - 2, col(FRAME_TL[i]));     // left
        fill(i + 1, i + h - 1, w - 1, 1, col(FRAME_BR[i])); // bottom
        fill(i + w - 1, i, 1, h - 1, col(FRAME_BR[i])); // right
    }

    // Grooves (2 px dark, 1 px light) across the face, splitting each side into corner handles.
    const double L = T - 2;
    if (W > NOTCH * 2 + 3) {
        for (double x : {(double)NOTCH, W - NOTCH - 3}) {
            fill(x, 1, 2, L, GROOVE_DARK), fill(x + 2, 1, 1, L, GROOVE_LIGHT);
            fill(x, H - T + 1, 2, L, GROOVE_DARK), fill(x + 2, H - T + 1, 1, L, GROOVE_LIGHT);
        }
    }
    if (H > NOTCH * 2 + 3) {
        for (double y : {(double)NOTCH, H - NOTCH - 3}) {
            fill(1, y, L, 2, GROOVE_DARK), fill(1, y + 2, L, 1, GROOVE_LIGHT);
            fill(W - T + 1, y, L, 2, GROOVE_DARK), fill(W - T + 1, y + 2, L, 1, GROOVE_LIGHT);
        }
    }

    m_seExtents        = {{(double)T, (double)T}, {(double)T, (double)T}};
    m_bLastRelativeBox = CBox{0, 0, m_lastWindowSize.x, m_lastWindowSize.y}.addExtents(m_seExtents);
}

eDecorationType CBordersPlusPlus::getDecorationType() {
    return DECORATION_CUSTOM;
}

void CBordersPlusPlus::updateWindow(PHLWINDOW pWindow) {
    m_lastWindowPos  = pWindow->position(Desktop::View::IGeometric::GEOMETRIC_CURRENT);
    m_lastWindowSize = pWindow->size(Desktop::View::IGeometric::GEOMETRIC_CURRENT);

    damageEntire();
}

void CBordersPlusPlus::damageEntire() {
    const auto PWINDOW = m_pWindow.lock();
    CBox       dm      = m_bLastRelativeBox.copy().translate(m_lastWindowPos);
    // The frame also wraps the title bar, so window + extents misses its top; use the assigned box.
    if (PWINDOW && validMapped(PWINDOW))
        dm = m_bAssignedGeometry.copy()
                 .translate(g_pDecorationPositioner->getEdgeDefinedPoint(DECORATION_EDGE_BOTTOM | DECORATION_EDGE_LEFT | DECORATION_EDGE_RIGHT | DECORATION_EDGE_TOP, PWINDOW))
                 .translate(PWINDOW->m_floatingOffset);
    g_pHyprRenderer->damageBox(dm.expand(2));
}
