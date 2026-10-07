# Generated wrapper for the same Python artifact; no bundled ML dependency tree.
class Mlca < Formula
  desc "Guided machine learning workflows with recorded provenance"
  homepage "https://pypi.org/project/mlcagent/"
  url "https://files.pythonhosted.org/packages/source/m/mlcagent/mlcagent-0.2.0b1.tar.gz"
  sha256 "3f91399736cb8a80a6a0208671928b39f6166726a2cc34feee632acd284b336f"
  version "0.2.0b1"

  depends_on "uv"

  def install
    (bin/"mlca").write <<~EOS
      #!/bin/sh
      exec "#{Formula["uv"].opt_bin}/uv" tool run --from "mlcagent==0.2.0b1" mlca "$@"
    EOS
  end

  test do
    assert_match "0.2.0b1", shell_output("#{bin}/mlca --version")
  end
end
