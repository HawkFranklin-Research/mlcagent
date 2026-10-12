# Generated wrapper for the same Python artifact; no bundled ML dependency tree.
class Mlca < Formula
  desc "Guided machine learning workflows with recorded provenance"
  homepage "https://pypi.org/project/mlcagent/"
  url "https://files.pythonhosted.org/packages/source/m/mlcagent/mlcagent-0.2.0b2.tar.gz"
  sha256 "c75b733acd0a66a09634524160d7615ee5d5ca0bb0ad1fb3308e876e0ec2a87b"
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
