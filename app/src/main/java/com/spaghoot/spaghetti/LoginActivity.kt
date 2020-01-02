package com.spaghoot.spaghetti

import android.content.Context
import android.content.Intent
import android.os.Bundle
import android.widget.Button
import androidx.appcompat.app.AppCompatActivity

class LoginActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_login)

        val preferences = this.getSharedPreferences(
            getString(R.string.preference_file_key), Context.MODE_PRIVATE
        )

        //val authToken = preferences.getString("auth_token", "none")
        //if (authToken != "none") {
        //    startActivity(Intent(this, MainActivity::class.java))
        //}

        val button = findViewById<Button>(R.id.login_button);
        button.setOnClickListener {
            // Save auth token
            with (preferences.edit()) {
                putString("auth_token", "debug_auth_token_value")
                apply()
            }
            // Go to main activity
            startActivity(Intent(this, MainActivity::class.java))
        }
    }
}