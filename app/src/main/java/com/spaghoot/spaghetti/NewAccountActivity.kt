package com.spaghoot.spaghetti

import android.os.Bundle
import androidx.appcompat.app.AppCompatActivity

class NewAccountActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_new_account)

        val accountType = intent.getStringExtra("spaghetti.account_type")
    }
}