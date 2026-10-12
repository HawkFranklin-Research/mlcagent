# Generated wrapper for the same Python artifact; no bundled ML dependency tree.
class Mlca < Formula
  desc "Guided machine learning workflows with recorded provenance"
  homepage "https://pypi.org/project/mlcagent/"
  url "https://files.pythonhosted.org/packages/source/m/mlcagent/mlcagent-0.2.0b2.tar.gz"
  sha256 "d74b43b1a1153c4df86177d24c17693041c9ea58eb2c3c875b308cf3885bf340"
  version "0.2.0b2"

  depends_on "uv"

  def install
    (bin/"mlca").write <<~EOS
      #!/bin/sh
      exec "#{Formula["uv"].opt_bin}/uv" tool run --from "mlcagent==0.2.0b2" mlca "$@"
    EOS
  end

  test do
    assert_match "0.2.0b2", shell_output("#{bin}/mlca --version")
  end
end
