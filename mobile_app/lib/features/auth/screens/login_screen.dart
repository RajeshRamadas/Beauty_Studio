import 'package:flutter/material.dart';
import '../../../core/network/api_client.dart';
import '../../../core/theme/app_theme.dart';

class LoginScreen extends StatefulWidget {
  final ApiClient apiClient;

  const LoginScreen({Key? key, required this.apiClient}) : super(key: key);

  @override
  State<LoginScreen> createState() => _LoginScreenState();
}

class _LoginScreenState extends State<LoginScreen> {
  final _emailController = TextEditingController();
  final _passwordController = TextEditingController();
  bool _isRegistering = false;
  bool _isLoading = false;
  String? _statusMessage;

  Future<void> _submit() async {
    final email = _emailController.text.trim();
    final password = _passwordController.text.trim();
    if (email.isEmpty || password.isEmpty) {
      setState(() {
        _statusMessage = "Please enter both email and password.";
      });
      return;
    }

    setState(() {
      _isLoading = true;
      _statusMessage = null;
    });

    try {
      if (_isRegistering) {
        await widget.apiClient.register(email, password);
        await widget.apiClient.login(email, password);
        setState(() {
          _statusMessage = "Account created & signed in!";
        });
      } else {
        await widget.apiClient.login(email, password);
        setState(() {
          _statusMessage = "Successfully signed in!";
        });
      }
    } catch (e) {
      setState(() {
        _statusMessage = "Auth failed: ${e.toString()}";
      });
    } finally {
      setState(() {
        _isLoading = false;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    final isSignedIn = widget.apiClient.authToken != null;

    return Scaffold(
      appBar: AppBar(title: const Text("Account & Auth")),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(20),
        child: Card(
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(18)),
          color: Colors.white,
          child: Padding(
            padding: const EdgeInsets.all(20),
            child: isSignedIn
                ? Column(
                    children: [
                      const Icon(Icons.check_circle, size: 60, color: Colors.green),
                      const SizedBox(height: 12),
                      const Text(
                        "Signed In",
                        style: TextStyle(fontSize: 22, fontWeight: FontWeight.bold),
                      ),
                      const SizedBox(height: 16),
                      ElevatedButton(
                        onPressed: () {
                          setState(() {
                            widget.apiClient.authToken = null;
                            _statusMessage = "Signed out.";
                          });
                        },
                        style: ElevatedButton.styleFrom(backgroundColor: Colors.grey[700]),
                        child: const Text("Sign Out"),
                      ),
                    ],
                  )
                : Column(
                    crossAxisAlignment: CrossAxisAlignment.stretch,
                    children: [
                      Text(
                        _isRegistering ? "Create an Account" : "Sign In to AI Beauty",
                        style: const TextStyle(fontSize: 20, fontWeight: FontWeight.bold),
                      ),
                      const SizedBox(height: 16),
                      TextField(
                        controller: _emailController,
                        decoration: const InputDecoration(
                          labelText: "Email address",
                          border: OutlineInputBorder(),
                        ),
                      ),
                      const SizedBox(height: 12),
                      TextField(
                        controller: _passwordController,
                        obscureText: true,
                        decoration: const InputDecoration(
                          labelText: "Password",
                          border: OutlineInputBorder(),
                        ),
                      ),
                      const SizedBox(height: 20),
                      ElevatedButton(
                        onPressed: _isLoading ? null : _submit,
                        child: Text(_isLoading ? "Processing..." : (_isRegistering ? "Register" : "Sign In")),
                      ),
                      TextButton(
                        onPressed: () {
                          setState(() {
                            _isRegistering = !_isRegistering;
                            _statusMessage = null;
                          });
                        },
                        child: Text(_isRegistering ? "Already have an account? Sign In" : "Need an account? Register"),
                      ),
                      if (_statusMessage != null) ...[
                        const SizedBox(height: 12),
                        Text(
                          _statusMessage!,
                          style: TextStyle(
                            color: _statusMessage!.contains("failed") ? Colors.red : Colors.green,
                          ),
                        ),
                      ],
                    ],
                  ),
          ),
        ),
      ),
    );
  }
}
