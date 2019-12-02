package com.spaghoot.spaghetti.ui.saving

import android.os.Bundle
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.TextView
import androidx.fragment.app.Fragment
import androidx.lifecycle.Observer
import androidx.lifecycle.ViewModelProviders
import com.spaghoot.spaghetti.R

class SavingFragment : Fragment() {

    private lateinit var savingViewModel: SavingViewModel

    override fun onCreateView(
        inflater: LayoutInflater,
        container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View? {
        savingViewModel =
            ViewModelProviders.of(this).get(SavingViewModel::class.java)
        val root = inflater.inflate(R.layout.fragment_saving, container, false)

        return root
    }
}