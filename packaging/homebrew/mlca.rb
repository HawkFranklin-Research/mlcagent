# Generated wrapper for the same Python artifact; no bundled ML dependency tree.
class Mlca < Formula
  desc "Guided machine learning workflows with recorded provenance"
  homepage "https://pypi.org/project/mlca/"
  url "https://files.pythonhosted.org/packages/source/m/mlca/mlca-0.2.0b1.tar.gz"
  sha256 "1dce0cda5540eaff393bd5e5ce2e6035d8ad3e5b8dc95789da55517cd809bbbe"
  version "0.2.0b1"

  depends_on "uv"

  def install
    (bin/"mlca").write <<~EOS
      #!/bin/sh
      exec "#{Formula["uv"].opt_bin}/uv" tool run --from "mlca==0.2.0b1" mlca "$@"
    EOS
  end

  test do
    assert_match "0.2.0b1", shell_output("#{bin}/mlca --version")
  end
end
