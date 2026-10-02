#include "../hyprbars/hourglass.hpp"
#include <cassert>
#include <iostream>
int main(int argc, char** argv) {
  assert(argc == 2);
  using namespace Classic98;
  for (auto s : {"⠋ Work", "⠴ Work", "⣿ Work"}) {
    auto t = agentTitle("org.omarchy.agent", s);
    assert(t.busy && t.text == "Work");
  }
  assert(!agentTitle("foot", "⠋ Work").busy);
  assert(agentTitle("foot", "⠋ Task | Project").busy);
  assert(!agentTitle("google-chrome", "⠋ Task | Project").busy);
  assert(!agentTitle("org.omarchy.agent", "Work").busy);
  assert(!agentTitle("org.omarchy.agent", "⠋Work").busy);
  { auto t = agentTitle("foot", "◑ Theme installation"); assert(t.busy && t.text == "Theme installation"); }
  assert(!agentTitle("foot", "◑Work").busy);
  assert(!agentTitle("google-chrome", "◑ Work").busy);
  { auto t = agentTitle("foot", "✳ Idle"); assert(!t.busy && t.text == "Idle"); }
  assert(agentTitle("google-chrome", "✳ Idle").text == "✳ Idle");
  auto a = loadHourglass(argv[1]);
  assert(a.frames.size() > 1 && a.durationMs > 0 && a.width > 0 && a.height > 0);
  assert(a.frameAt(0) == 0 && a.frameAt(a.durationMs) == 0);
  assert(a.frameAt(a.frames[0].delayMs) == 1);
  assert(a.frames[0].rgba != a.frames[1].rgba);
  bool transparent = false, opaqueWhite = false;
  for (size_t i=0; i<a.frames[0].rgba.size(); i+=4) {
    const auto& p = a.frames[0].rgba;
    transparent |= p[i+3] == 0;
    opaqueWhite |= p[i] >= 245 && p[i+1] >= 245 && p[i+2] >= 245 && p[i+3] == 255;
  }
  assert(transparent && opaqueWhite);
  assert(loadHourglass("/tmp/missing-hourglass.gif").frames.empty());
  std::cout << a.frames.size() << " frames; " << a.durationMs << " ms; visible canvas " << a.width << "x" << a.height << "\nAll checks passed\n";
}
