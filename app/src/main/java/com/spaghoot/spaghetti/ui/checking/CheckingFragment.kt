package com.spaghoot.spaghetti.ui.checking

import android.os.Bundle
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.TextView
import androidx.fragment.app.Fragment
import androidx.lifecycle.Observer
import androidx.lifecycle.ViewModelProviders
import com.spaghoot.spaghetti.R

class CheckingFragment : Fragment() {

    private lateinit var checkingViewModel: CheckingViewModel

    override fun onCreateView(
        inflater: LayoutInflater,
        container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View? {
        checkingViewModel =
            ViewModelProviders.of(this).get(CheckingViewModel::class.java)
        val root = inflater.inflate(R.layout.fragment_checking, container, false)

        return root
    }
}