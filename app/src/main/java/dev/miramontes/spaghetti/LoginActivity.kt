package dev.miramontes.spaghetti

import android.content.Context
import android.content.Intent
import android.os.Bundle
import android.util.Log
import android.widget.Button
import android.widget.EditText
import androidx.appcompat.app.AppCompatActivity

class LoginActivity : AppCompatActivity() {
    private fun onLoginResponse(response: String) {
        val preferences = this.getSharedPreferences(
            getString(R.string.preference_file_key), Context.MODE_PRIVATE
        )

        with (preferences.edit()) {
            putString("username", "debug_auth_username")
            putString("auth_token", "debug_auth_token_value")
            apply()
        }

        Log.i("Response", response)
        startActivity(Intent(this, MainActivity::class.java))
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_login)

        val usernameEntry = findViewById<EditText>(R.id.username_entry)
        val passwordEntry = findViewById<EditText>(R.id.password_entry)

        val loginButton = findViewById<Button>(R.id.login_button)
        loginButton.setOnClickListener {
            val postParams = HashMap<String, String>()
            postParams["username"] = usernameEntry.text.toString()
            postParams["password"] = passwordEntry.text.toString()
            onLoginResponse("Debug Response")
        }

        val registerButton = findViewById<Button>(R.id.register_button)
        registerButton.setOnClickListener {
            val postParams = HashMap<String, String>()
            postParams["username"] = usernameEntry.text.toString()
            postParams["password"] = passwordEntry.text.toString()
            onLoginResponse("Debug Response")
        }
    }
}